# 배지 시스템 디자인 가이드

## 📊 현재 구현 상태

현재 배지 시스템은 **문자열 ID만 반환**합니다:
```json
{
  "achievement_badges": [
    "first_entry",
    "first_week",
    "streak_week"
  ]
}
```

실제 이미지나 아이콘은 **아직 구현되지 않았습니다**. 프론트엔드에서 배지 ID를 받아서 이미지/아이콘을 매핑해야 합니다.

---

## 🎨 배지 디자인 컨셉 제안

### 전체적인 느낌
- **스타일**: 미니멀하고 따뜻한 느낌
- **컬러**: 부드러운 파스텔 톤 또는 그라데이션
- **아이콘**: 일기/성찰과 관련된 심볼 (펜, 별, 하트, 불꽃 등)
- **등급**: 배지의 희귀도에 따라 색상/효과 차별화

---

## 🏆 배지별 디자인 제안

### 1. **first_entry** - 첫 일기 작성
**컨셉**: 시작의 의미  
**디자인**:
- 아이콘: ✍️ 펜 또는 📝 노트
- 색상: 연한 파란색 (#B3E5FC)
- 느낌: 부드럽고 격려하는 느낌
- 텍스트: "첫 걸음"

---

### 2. **first_week** - 첫 주 완성 (7일)
**컨셉**: 꾸준함의 시작  
**디자인**:
- 아이콘: ⭐ 별 또는 🌱 새싹
- 색상: 연한 초록색 (#C8E6C9)
- 느낌: 성장하는 느낌
- 텍스트: "일주일의 기적"

---

### 3. **one_month** - 한 달 완성 (30일)
**컨셉**: 습관 형성  
**디자인**:
- 아이콘: 🌙 달 또는 📅 캘린더
- 색상: 연한 보라색 (#E1BEE7)
- 느낌: 안정감 있는 느낌
- 텍스트: "한 달의 여정"

---

### 4. **hundred_days** - 100일 달성
**컨셉**: 큰 성취  
**디자인**:
- 아이콘: 💯 100 또는 🏆 트로피
- 색상: 골드/황금색 (#FFD700)
- 느낌: 화려하고 축하하는 느낌
- 텍스트: "백일의 기적"
- 효과: 반짝이는 애니메이션 가능

---

### 5. **streak_week** - 7일 연속 기록
**컨셉**: 연속성의 힘  
**디자인**:
- 아이콘: 🔥 불꽃 또는 ⚡ 번개
- 색상: 주황색/빨간색 (#FF9800)
- 느낌: 열정적이고 동기부여하는 느낌
- 텍스트: "7일 연속!"
- 효과: 불꽃 애니메이션 가능

---

### 6. **streak_month** - 30일 연속 기록
**컨셉**: 강력한 습관  
**디자인**:
- 아이콘: 🔥🔥 더블 불꽃 또는 ⭐⭐ 별
- 색상: 진한 주황색 (#FF6B00)
- 느낌: 강렬하고 인상적인 느낌
- 텍스트: "30일 연속!"
- 효과: 더 강한 불꽃 효과

---

### 7. **streak_century** - 100일 연속 기록
**컨셉**: 전설적인 기록  
**디자인**:
- 아이콘: 👑 왕관 또는 🔥🔥🔥 트리플 불꽃
- 색상: 골드 + 빨간색 그라데이션
- 느낌: 매우 특별하고 희귀한 느낌
- 텍스트: "100일 연속!"
- 효과: 황금 불꽃 + 반짝임 애니메이션

---

### 8. **legendary_streak** - 최장 기록 30일 이상
**컨셉**: 전설의 시작  
**디자인**:
- 아이콘: ⚡ 번개 또는 🌟 별
- 색상: 보라색/자주색 (#9C27B0)
- 느낌: 신비롭고 특별한 느낌
- 텍스트: "전설의 기록"

---

### 9. **master_streaker** - 최장 기록 100일 이상
**컨셉**: 마스터 레벨  
**디자인**:
- 아이콘: 👑 황금 왕관 또는 💎 다이아몬드
- 색상: 골드 + 다이아몬드 효과
- 느낌: 최고 등급, 매우 희귀
- 텍스트: "마스터"
- 효과: 다이아몬드 반짝임 + 황금 효과

---

## 🎨 디자인 가이드라인

### 색상 팔레트
```
기본 (Bronze): #CD7F32 (구리색)
은색 (Silver): #C0C0C0
금색 (Gold): #FFD700
플래티넘 (Platinum): #E5E4E2
다이아몬드 (Diamond): #B9F2FF
```

### 등급별 색상 매핑
- **일반 배지** (first_entry, first_week): 파스텔 톤
- **중급 배지** (one_month, streak_week): 밝은 색상
- **고급 배지** (hundred_days, streak_month): 진한 색상
- **전설 배지** (streak_century, legendary_streak): 골드/보라색
- **마스터 배지** (master_streaker): 다이아몬드 효과

---

## 💻 프론트엔드 구현 예시

### 배지 ID → 이미지 매핑
```javascript
const badgeImages = {
  "first_entry": "/badges/first_entry.svg",
  "first_week": "/badges/first_week.svg",
  "one_month": "/badges/one_month.svg",
  "hundred_days": "/badges/hundred_days.svg",
  "streak_week": "/badges/streak_week.svg",
  "streak_month": "/badges/streak_month.svg",
  "streak_century": "/badges/streak_century.svg",
  "legendary_streak": "/badges/legendary_streak.svg",
  "master_streaker": "/badges/master_streaker.svg"
};
```

### 배지 표시 예시
```jsx
{achievement_badges.map(badgeId => (
  <Badge 
    key={badgeId}
    icon={badgeImages[badgeId]}
    name={badgeNames[badgeId]}
    rarity={getBadgeRarity(badgeId)}
  />
))}
```

---

## 🚀 향후 개선 방안

### 1. 배지 메타데이터 API 추가
```json
GET /api/badges
{
  "badges": [
    {
      "id": "first_entry",
      "name": "첫 걸음",
      "description": "첫 일기를 작성했습니다",
      "icon_url": "/badges/first_entry.svg",
      "rarity": "common",
      "unlocked_at": "2024-01-01"
    }
  ]
}
```

### 2. 배지 상세 정보 API
```json
GET /api/badges/{badge_id}
{
  "id": "streak_century",
  "name": "100일 연속!",
  "description": "100일 연속으로 일기를 작성했습니다",
  "icon_url": "/badges/streak_century.svg",
  "rarity": "legendary",
  "unlocked_at": "2024-04-10",
  "unlocked_count": 123  // 전체 사용자 중 달성한 사람 수
}
```

### 3. 배지 이미지 제공
- SVG 아이콘 제공 (확대해도 깨지지 않음)
- PNG/SVG 파일을 `/static/badges/` 경로에 저장
- 또는 CDN 사용

---

## 📝 배지 이름 한글화

현재는 영어 ID만 있지만, 프론트엔드에서 한글 이름 매핑:

```javascript
const badgeNames = {
  "first_entry": "첫 걸음",
  "first_week": "일주일의 기적",
  "one_month": "한 달의 여정",
  "hundred_days": "백일의 기적",
  "streak_week": "7일 연속!",
  "streak_month": "30일 연속!",
  "streak_century": "100일 연속!",
  "legendary_streak": "전설의 기록",
  "master_streaker": "마스터"
};
```

---

## 🎯 요약

**현재 상태**: 배지 ID 문자열만 반환  
**디자인 컨셉**: 미니멀하고 따뜻한 느낌, 등급별 색상 차별화  
**다음 단계**: 
1. 배지 메타데이터 API 추가 (이름, 설명, 아이콘 URL)
2. 배지 이미지/아이콘 제작
3. 프론트엔드에서 배지 시각화

**추천**: 먼저 배지 메타데이터 API를 추가하여 프론트엔드에서 쉽게 활용할 수 있도록 하는 것이 좋습니다!


