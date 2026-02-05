/**
 * 대시보드 데이터 관리 Composable
 */
import { ref, computed, onMounted, onUnmounted, watch } from "vue";
import {
  fetchDashboardStats,
  fetchWaybills,
  fetchDailyStats,
  fetchAlerts,
  getExportUrl,
  fetchOcrResults,
} from "../api";
import { STATUS_MAP, STATUS_PRIORITY, CITIES, CHART_COLORS, POLLING_INTERVALS } from "../constants";
import { getToday } from "../utils/date";

export function useDashboard() {
  // 날짜 설정
  const maxDate = ref(getToday());
  const selectedDate = ref(getToday());

  // 반응형 데이터
  const chartSeries = ref([]);
  const logisticsData = ref([]);
  const latestScan = ref(null);
  const chartMax = ref(10);
  const isLoading = ref(false);
  const error = ref(null);

  // 추가 통계 데이터
  const dailyStats = ref(null);
  const alerts = ref([]);
  const todaySummary = ref({
    total: 0,
    completed: 0,
    error: 0,
    avgProcessTime: null,
    successRate: 0,
  });

  // 필터
  const filterRegion = ref("전체");
  const filterStatus = ref("전체");

  // 폴링 인터벌 및 WebSocket
  let refreshInterval = null;
  let wsConnection = null;

  /**
   * 대시보드 데이터 로드
   */
  const loadData = async () => {
    isLoading.value = true;
    error.value = null;

    try {
      // 구역별 통계, 운송장 목록, 일별 통계, 알림, OCR 결과를 병렬로 호출
      // 날짜 필터링: 오늘 날짜인 경우 UTC 시차 문제로 데이터가 안 보일 수 있으므로
      // 날짜 필터를 제거하여 최근 데이터를 가져오도록 함
      const waybillParams = { size: 100 };
      if (selectedDate.value && selectedDate.value !== getToday()) {
        waybillParams.date = selectedDate.value;
      }

      const results = await Promise.allSettled([
        fetchDashboardStats(selectedDate.value),
        fetchWaybills(waybillParams),
        fetchDailyStats(selectedDate.value, selectedDate.value),
        fetchAlerts({ resolved: false, size: 50 }),
        fetchOcrResults(50),
      ]);

      const statsRes =
        results[0].status === "fulfilled" ? results[0].value : { data: { data: [] } };
      const waybillsRes =
        results[1].status === "fulfilled" ? results[1].value : { data: { data: { items: [] } } };
      const dailyRes =
        results[2].status === "fulfilled" ? results[2].value : { data: { data: [] } };
      const alertsRes =
        results[3].status === "fulfilled" ? results[3].value : { data: { data: [] } };
      const ocrRes =
        results[4].status === "fulfilled" ? results[4].value : { data: { data: { items: [] } } };

      // Log errors if any
      results.forEach((res, index) => {
        if (res.status === "rejected") {
          console.error(`API call ${index} failed:`, res.reason);
        }
      });

      // 구역별 통계 처리
      const regionStats = statsRes.data.data || [];
      let totalDone = 0;
      let totalLeft = 0;
      let totalError = 0;
      let totalAll = 0;
      const finishedArr = [];
      const pendingArr = [];

      CITIES.forEach((city) => {
        const cityData = regionStats.find((r) => r.region_name === city) || {
          completed: 0,
          ready: 0,
          moving: 0,
          error: 0,
        };
        const done = Number(cityData.completed || 0);
        const left = Number(cityData.ready || 0) + Number(cityData.moving || 0);
        const err = Number(cityData.error || 0);

        finishedArr.push({ x: city, y: done, fillColor: CHART_COLORS.completed });
        // pending: amber-500 (#f59e0b)
        pendingArr.push({ x: city, y: left + err, fillColor: "#f59e0b" });

        totalDone += done;
        totalLeft += left;
        totalError += err;
        totalAll += done + left + err;
      });

      // 전체 데이터 추가 (맨 앞)
      finishedArr.unshift({ x: "전체", y: totalDone, fillColor: CHART_COLORS.totalCompleted });
      pendingArr.unshift({ x: "전체", y: totalLeft + totalError, fillColor: "#f59e0b" });

      // Y축 최대값 계산
      const allValues = [...finishedArr.map((d) => d.y), ...pendingArr.map((d) => d.y)];
      const maxVal = Math.max(...allValues);
      chartMax.value = maxVal > 0 ? maxVal : 5;

      // 차트 시리즈 설정
      chartSeries.value = [
        { name: "완료 건수", data: finishedArr },
        { name: "남은 건수", data: pendingArr },
      ];

      // 일별 통계 처리
      const dailyData = dailyRes.data.data?.[0] || null;
      dailyStats.value = dailyData;

      // 운송장 목록 처리
      const waybillItems = waybillsRes.data.data?.items || [];
      const waybillData = waybillItems.map((item) => ({
        id: item.tracking_number,
        waybillId: item.waybill_id,
        target: item.destination || "-",
        status: STATUS_MAP[item.status] || item.status,
        rawStatus: item.status,
        dateTime: item.completed_at || item.created_at || "",
        processTime: item.process_time_sec || null,
        confidenceScore: item.confidence_score || null,
      }));

      // OCR 결과 처리 및 병합 (필터링 최소화)
      const ocrItems = ocrRes.data?.data?.items || [];
      const existingTrackingNumbers = new Set(waybillData.map((item) => item.id));

      const ocrData = ocrItems
        .filter((ocrItem) => !existingTrackingNumbers.has(ocrItem.tracking_number)) // 중복만 제거
        .map((ocrItem) => ({
          id: ocrItem.tracking_number,
          waybillId: ocrItem.result_id || `OCR-${Date.now()}`,
          target: ocrItem.region_code || "-",
          // status: 'completed'를 '대기 중'으로 매핑하지 않고 원본 값 사용하거나 매핑
          status: "대기 중",
          rawStatus: "ready",
          dateTime: ocrItem.processed_at || new Date().toISOString(),
          processTime: null,
          confidenceScore: null,
          recipientName: ocrItem.recipient_name,
          recipientAddress: ocrItem.recipient_address,
          senderName: ocrItem.sender_name,
          senderAddress: ocrItem.sender_address,
          isFromOcr: true,
        }));

      console.log("Waybill Data:", waybillData.length);
      console.log("OCR Data:", ocrData.length);

      // waybill 데이터와 OCR 데이터 병합
      logisticsData.value = [...ocrData, ...waybillData];

      // 오늘 요약 정보 업데이트 (실시간 데이터 반영을 위해 frontend 계산 사용)
      const allItemsForSummary = [...ocrData, ...waybillItems];
      const summaryTotal = allItemsForSummary.length;
      const summaryCompleted = allItemsForSummary.filter((i) => i.status === "완료").length;
      const summaryError = allItemsForSummary.filter((i) => i.status === "오류").length;

      todaySummary.value = {
        total: summaryTotal,
        completed: summaryCompleted,
        error: summaryError,
        avgProcessTime: dailyData?.avg_process_time_sec || null,
        successRate: summaryTotal > 0 ? Math.round((summaryCompleted / summaryTotal) * 100) : 0,
      };

      // 알림 데이터
      alerts.value = alertsRes.data.data?.items || alertsRes.data.data || [];

      // 최근 인식 정보 (OCR 또는 waybill 데이터 활용)
      const allItems = [...ocrData, ...waybillItems];
      if (allItems.length > 0) {
        const recentItem = ocrData.length > 0 ? ocrData[0] : waybillItems[0];
        if (ocrData.length > 0) {
          latestScan.value = {
            waybillId: recentItem.waybillId,
            destination: recentItem.target,
            matchRate: "-",
            camId: "CAM:OCR",
            waybill: recentItem.id,
            status: recentItem.rawStatus,
            processTime: null,
            scannedAt: recentItem.dateTime,
          };
        } else if (waybillItems.length > 0) {
          latestScan.value = {
            waybillId: waybillItems[0].waybill_id,
            destination: waybillItems[0].destination || "-",
            matchRate: waybillItems[0].confidence_score
              ? `${waybillItems[0].confidence_score.toFixed(1)}%`
              : "-",
            camId: "CAM:01",
            waybill: waybillItems[0].tracking_number,
            status: waybillItems[0].status,
            processTime: waybillItems[0].process_time_sec,
            scannedAt: waybillItems[0].created_at,
          };
        }
      } else {
        latestScan.value = null;
      }
    } catch (err) {
      console.error("데이터 로드 실패:", err);
      error.value = err.message || "데이터를 불러오는데 실패했습니다.";
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * 엑셀 다운로드
   */
  const downloadExcel = () => {
    const url = getExportUrl(selectedDate.value);
    window.open(url, "_blank");
  };

  /**
   * 필터링된 물류 데이터 (computed)
   */
  const filteredLogisticsData = computed(() => {
    // 디버깅을 위해 클라이언트 사이드 필터링을 잠시 비활성화하고 전체 데이터 반환
    // 나중에 다시 활성화하되, 지금은 데이터를 보이게 하는 것이 최우선
    return logisticsData.value;

    /* 기존 필터링 로직 주석 처리
    const filtered = logisticsData.value.filter(item => {
      const regionMatch = filterRegion.value === '전체' || item.target === filterRegion.value
      const statusMatch = filterStatus.value === '전체' || item.status === filterStatus.value
      return regionMatch && statusMatch
    })

    return filtered.sort((a, b) => {
      const priorityA = STATUS_PRIORITY[a.status] || 99
      const priorityB = STATUS_PRIORITY[b.status] || 99

      if (priorityA !== priorityB) return priorityA - priorityB
      if (a.dateTime < b.dateTime) return 1
      if (a.dateTime > b.dateTime) return -1
      return 0
    })
    */
  });

  /**
   * 폴링 시작
   */
  const startPolling = () => {
    stopPolling();
    refreshInterval = setInterval(loadData, POLLING_INTERVALS.dashboard);
  };

  /**
   * 폴링 중지
   */
  const stopPolling = () => {
    if (refreshInterval) {
      clearInterval(refreshInterval);
      refreshInterval = null;
    }
  };

  /**
   * OCR 결과를 물류 테이블에 추가 (WebSocket으로 받은 실시간 데이터)
   */
  const addOcrResultToLogistics = (payload) => {
    // status check: allow 'completed' (from OCR) or 'ready' (from Waybill update)
    if (!payload || (payload.status !== "completed" && payload.status !== "ready")) return;

    // 중복 체크
    const exists = logisticsData.value.some((item) => item.id === payload.tracking_number);
    if (exists) return;

    const newItem = {
      id: payload.tracking_number,
      waybillId: payload.result_id || `OCR-${Date.now()}`,
      target: payload.region_code || "-",
      status: "대기 중",
      rawStatus: "ready",
      dateTime: payload.processed_at || new Date().toISOString(),
      processTime: null,
      confidenceScore: null,
      // OCR 추가 정보
      recipientName: payload.recipient_name || null,
      recipientAddress: payload.recipient_address || null,
      senderName: payload.sender_name || null,
      senderAddress: payload.sender_address || null,
      isFromOcr: true, // OCR에서 온 데이터임을 표시
    };

    // 맨 앞에 추가
    logisticsData.value.unshift(newItem);

    // 최신 스캔 정보 업데이트
    latestScan.value = {
      waybillId: newItem.waybillId,
      destination: newItem.target,
      matchRate: "-",
      camId: "CAM:OCR",
      waybill: newItem.id,
      status: newItem.rawStatus,
      processTime: null,
      scannedAt: newItem.dateTime,
    };

    // 오늘 요약 업데이트
    todaySummary.value.total += 1;
  };

  /**
   * WebSocket 연결 설정
   */
  const setupWebSocket = () => {
    try {
      const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const wsUrl = `${wsProtocol}//${window.location.host}/ws`;

      wsConnection = new WebSocket(wsUrl);

      wsConnection.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          if (message.type === "ocr_result") {
            // OCR 결과를 물류 테이블에 자동 추가
            addOcrResultToLogistics(message.payload);
          } else if (message.type === "waybill_update") {
            // 물류 상태 업데이트 (OCR 저장 후 발생)
            const data = message.data;
            // 중복 방지를 위해 이미 있는지 확인하고 없으면 추가, 있으면 업데이트?
            // 여기서는 addOcrResultToLogistics 재사용하거나 비슷하게 처리
            // 하지만 payload 구조가 다르므로 매핑 필요
            const mappedPayload = {
              tracking_number: data.tracking_number,
              result_id: String(data.waybill_id),
              region_code: data.destination,
              status: "ready", // OCR 직후는 ready
              processed_at: new Date().toISOString(),
            };
            // addOcrResultToLogistics 내부에서 중복 체크하므로 호출
            addOcrResultToLogistics(mappedPayload);
          }
        } catch (e) {
          console.debug("WebSocket message parse error:", e);
        }
      };

      wsConnection.onclose = () => {
        console.debug("WebSocket closed, attempting reconnect in 5s");
        setTimeout(setupWebSocket, 5000);
      };

      wsConnection.onerror = (error) => {
        console.debug("WebSocket error:", error);
      };
    } catch (error) {
      console.debug("WebSocket connection failed:", error);
    }
  };

  /**
   * WebSocket 연결 종료
   */
  const closeWebSocket = () => {
    if (wsConnection) {
      wsConnection.close();
      wsConnection = null;
    }
  };

  // 날짜 변경 감시
  watch(selectedDate, () => {
    loadData();
  });

  // 컴포넌트 마운트 시 초기화
  onMounted(() => {
    loadData();
    startPolling();
    setupWebSocket(); // WebSocket 연결 시작
  });

  // 컴포넌트 언마운트 시 정리
  onUnmounted(() => {
    stopPolling();
    closeWebSocket(); // WebSocket 연결 종료
  });

  return {
    // 상태
    maxDate,
    selectedDate,
    chartSeries,
    chartMax,
    logisticsData,
    filteredLogisticsData,
    latestScan,
    isLoading,
    error,

    // 추가 통계
    dailyStats,
    alerts,
    todaySummary,

    // 필터
    filterRegion,
    filterStatus,

    // 메서드
    loadData,
    startPolling,
    stopPolling,
    downloadExcel,
  };
}
