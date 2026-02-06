# 배지 시스템 프론트엔드 매핑 가이드

## 📋 개요

현재 백엔드는 배지 ID 문자열 리스트만 반환합니다. 프론트엔드에서 이 ID를 받아서 이름, 아이콘, 색상 등을 매핑하여 표시해야 합니다.

---

## 🔌 API 응답 형식

```json
GET /api/analytics/streak
{
  "current_streak": 7,
  "longest_streak": 21,
  "total_days": 45,
  "achievement_badges": [
    "first_entry",
    "first_week",
    "streak_week"
  ]
}
```

---

## 🗺️ 배지 ID → 정보 매핑

### JavaScript/TypeScript 예시

```typescript
// 배지 정보 타입 정의
interface BadgeInfo {
  id: string;
  name: string;
  description: string;
  icon: string;  // 이모지 또는 아이콘 이름
  color: string;  // HEX 색상 코드
  rarity: 'common' | 'rare' | 'epic' | 'legendary' | 'master';
}

// 배지 정보 매핑
const BADGE_MAP: Record<string, BadgeInfo> = {
  // 기본 달성 배지
  "first_entry": {
    id: "first_entry",
    name: "첫 걸음",
    description: "첫 일기를 작성했습니다",
    icon: "✍️",
    color: "#B3E5FC",
    rarity: "common"
  },
  "first_week": {
    id: "first_week",
    name: "일주일의 기적",
    description: "7일 동안 일기를 작성했습니다",
    icon: "⭐",
    color: "#C8E6C9",
    rarity: "common"
  },
  "one_month": {
    id: "one_month",
    name: "한 달의 여정",
    description: "30일 동안 일기를 작성했습니다",
    icon: "🌙",
    color: "#E1BEE7",
    rarity: "rare"
  },
  "hundred_days": {
    id: "hundred_days",
    name: "백일의 기적",
    description: "100일 동안 일기를 작성했습니다",
    icon: "💯",
    color: "#FFD700",
    rarity: "epic"
  },
  
  // 연속 기록 배지
  "streak_week": {
    id: "streak_week",
    name: "7일 연속!",
    description: "7일 연속으로 일기를 작성했습니다",
    icon: "🔥",
    color: "#FF9800",
    rarity: "rare"
  },
  "streak_month": {
    id: "streak_month",
    name: "30일 연속!",
    description: "30일 연속으로 일기를 작성했습니다",
    icon: "🔥🔥",
    color: "#FF6B00",
    rarity: "epic"
  },
  "streak_century": {
    id: "streak_century",
    name: "100일 연속!",
    description: "100일 연속으로 일기를 작성했습니다",
    icon: "👑",
    color: "#FFD700",
    rarity: "legendary"
  },
  
  // 최장 기록 배지
  "legendary_streak": {
    id: "legendary_streak",
    name: "전설의 기록",
    description: "최장 연속 기록이 30일 이상입니다",
    icon: "⚡",
    color: "#9C27B0",
    rarity: "legendary"
  },
  "master_streaker": {
    id: "master_streaker",
    name: "마스터",
    description: "최장 연속 기록이 100일 이상입니다",
    icon: "💎",
    color: "#B9F2FF",
    rarity: "master"
  }
};

// 배지 정보 조회 함수
export function getBadgeInfo(badgeId: string): BadgeInfo | null {
  return BADGE_MAP[badgeId] || null;
}

// 배지 리스트를 정보로 변환
export function getBadgeInfos(badgeIds: string[]): BadgeInfo[] {
  return badgeIds
    .map(id => getBadgeInfo(id))
    .filter((info): info is BadgeInfo => info !== null);
}
```

---

## 🎨 React 컴포넌트 예시

```tsx
// Badge.tsx
import React from 'react';
import { getBadgeInfo } from './badgeMapping';

interface BadgeProps {
  badgeId: string;
  size?: 'small' | 'medium' | 'large';
}

export const Badge: React.FC<BadgeProps> = ({ badgeId, size = 'medium' }) => {
  const badgeInfo = getBadgeInfo(badgeId);
  
  if (!badgeInfo) return null;
  
  const sizeClasses = {
    small: 'w-8 h-8 text-xs',
    medium: 'w-12 h-12 text-base',
    large: 'w-16 h-16 text-xl'
  };
  
  return (
    <div
      className={`${sizeClasses[size]} rounded-full flex items-center justify-center shadow-md`}
      style={{ backgroundColor: badgeInfo.color }}
      title={badgeInfo.description}
    >
      <span className="text-2xl">{badgeInfo.icon}</span>
    </div>
  );
};

// BadgeList.tsx
interface BadgeListProps {
  badgeIds: string[];
}

export const BadgeList: React.FC<BadgeListProps> = ({ badgeIds }) => {
  return (
    <div className="flex flex-wrap gap-2">
      {badgeIds.map(badgeId => (
        <Badge key={badgeId} badgeId={badgeId} />
      ))}
    </div>
  );
};
```

---

## 🎨 CSS 스타일 예시

```css
/* 배지 기본 스타일 */
.badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  transition: transform 0.2s;
}

.badge:hover {
  transform: scale(1.1);
}

/* 등급별 스타일 */
.badge-common {
  border: 2px solid #B3E5FC;
}

.badge-rare {
  border: 2px solid #C8E6C9;
  box-shadow: 0 2px 12px rgba(200, 230, 201, 0.4);
}

.badge-epic {
  border: 2px solid #FF9800;
  box-shadow: 0 2px 16px rgba(255, 152, 0, 0.5);
}

.badge-legendary {
  border: 3px solid #FFD700;
  box-shadow: 0 4px 20px rgba(255, 215, 0, 0.6);
  animation: glow 2s ease-in-out infinite;
}

.badge-master {
  border: 3px solid #B9F2FF;
  box-shadow: 0 4px 24px rgba(185, 242, 255, 0.7);
  animation: diamond-glow 2s ease-in-out infinite;
}

@keyframes glow {
  0%, 100% { box-shadow: 0 4px 20px rgba(255, 215, 0, 0.6); }
  50% { box-shadow: 0 4px 30px rgba(255, 215, 0, 0.9); }
}

@keyframes diamond-glow {
  0%, 100% { box-shadow: 0 4px 24px rgba(185, 242, 255, 0.7); }
  50% { box-shadow: 0 4px 35px rgba(185, 242, 255, 1); }
}
```

---

## 📱 모바일 최적화 예시

```tsx
// 모바일에서 배지 그리드 표시
export const BadgeGrid: React.FC<{ badgeIds: string[] }> = ({ badgeIds }) => {
  return (
    <div className="grid grid-cols-4 gap-4 p-4">
      {badgeIds.map(badgeId => {
        const badge = getBadgeInfo(badgeId);
        if (!badge) return null;
        
        return (
          <div key={badgeId} className="flex flex-col items-center">
            <Badge badgeId={badgeId} size="medium" />
            <span className="text-xs mt-1 text-center">{badge.name}</span>
          </div>
        );
      })}
    </div>
  );
};
```

---

## 🎯 배지 표시 우선순위

배지를 표시할 때는 등급(rarity)에 따라 정렬하는 것을 추천합니다:

```typescript
const RARITY_ORDER = {
  'master': 5,
  'legendary': 4,
  'epic': 3,
  'rare': 2,
  'common': 1
};

export function sortBadgesByRarity(badgeIds: string[]): string[] {
  return badgeIds.sort((a, b) => {
    const infoA = getBadgeInfo(a);
    const infoB = getBadgeInfo(b);
    if (!infoA || !infoB) return 0;
    return RARITY_ORDER[infoB.rarity] - RARITY_ORDER[infoA.rarity];
  });
}
```

---

## 📊 배지 통계 표시 예시

```tsx
// 사용자가 획득한 배지와 미획득 배지 표시
export const BadgeCollection: React.FC<{ userBadges: string[] }> = ({ userBadges }) => {
  const allBadges = Object.keys(BADGE_MAP);
  const unlockedBadges = allBadges.filter(id => userBadges.includes(id));
  const lockedBadges = allBadges.filter(id => !userBadges.includes(id));
  
  return (
    <div>
      <h3>획득한 배지 ({unlockedBadges.length}/{allBadges.length})</h3>
      <BadgeList badgeIds={unlockedBadges} />
      
      <h3>미획득 배지</h3>
      <div className="opacity-50">
        <BadgeList badgeIds={lockedBadges} />
      </div>
    </div>
  );
};
```

---

## 🎨 아이콘 대체 옵션

이모지 대신 아이콘 라이브러리를 사용할 수도 있습니다:

### React Icons 사용 예시
```tsx
import { FaPen, FaStar, FaFire, FaCrown, FaGem } from 'react-icons/fa';

const badgeIcons = {
  "first_entry": <FaPen />,
  "first_week": <FaStar />,
  "streak_week": <FaFire />,
  "streak_century": <FaCrown />,
  "master_streaker": <FaGem />
};
```

### Material Icons 사용 예시
```tsx
import { Edit, Star, LocalFireDepartment, EmojiEvents, Diamond } from '@mui/icons-material';

const badgeIcons = {
  "first_entry": <Edit />,
  "first_week": <Star />,
  "streak_week": <LocalFireDepartment />,
  "streak_century": <EmojiEvents />,
  "master_streaker": <Diamond />
};
```

---

## 📝 요약

1. **백엔드**: 배지 ID 문자열 리스트만 반환
2. **프론트엔드**: ID를 받아서 이름, 아이콘, 색상 매핑
3. **표시**: 등급별 스타일 적용, 정렬, 애니메이션 등

이 가이드를 참고하여 프론트엔드에서 배지를 구현하시면 됩니다!


