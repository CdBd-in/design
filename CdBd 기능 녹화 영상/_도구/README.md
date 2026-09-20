# 프레임 추출기

> 🔧 **이 맥에는 `ffmpeg`가 없다.** Swift/AVFoundation으로 만든 대체 도구.

## 빌드 (최초 1회)
```
swiftc -O -o /tmp/extract "CdBd 기능 녹화 영상/_도구/프레임추출기.swift"
```

## 사용
```
/tmp/extract <입력.mov> <출력폴더> <간격초> <영상길이초> <최대폭px>
```
예: `/tmp/extract "동선3.mov" /tmp/f 2 150 2000`

- 영상 길이는 `mdls -raw -name kMDItemDurationSeconds "파일.mov"` 로 얻는다
- 출력 파일명 = `tNNNN.N.jpg` (영상 내 초)
- 권장값: 간격 **2초**, 최대폭 **2000px** (UI 문구 판독 가능)

## 판독 시 주의
- 🔑 **호버 툴팁**은 2초 간격에서 놓치기 쉽다 — 촬영 때 **커서를 올린 채 3초 정지**할 것
- 🔑 **다운로드 바**도 마찬가지 — 받은 뒤 **화면 하단을 3초** 잡을 것
