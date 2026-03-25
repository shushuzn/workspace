import { useState, useEffect } from 'react';
import styles from './Tutorial.module.css';

const TUTORIAL_STEPS = [
  {
    id: 'welcome',
    title: '🌟 欢迎来到星之熔炉！',
    content: '点击太阳收获能量，建立你的宇宙帝国！快速连击可获得更高加成。',
    icon: '⚡',
    target: 'clickArea',
    position: 'center',
  },
  {
    id: 'buildings',
    title: '🏗️ 建筑系统',
    content: '购买建筑自动产生能量。每个建筑每秒产出能量，越高级的建筑产出越高！',
    icon: '☀️',
    target: 'tab-buildings',
    position: 'bottom',
  },
  {
    id: 'firstBuilding',
    title: '💰 购买第一个建筑',
    content: '太阳能板是最便宜的建筑，购买后立即开始产出能量！攒够能量购买更多建筑。',
    icon: '🌞',
    target: 'building-solar_panel',
    position: 'right',
  },
  {
    id: 'upgrades',
    title: '⬆️ 升级系统',
    content: '升级可以提升建筑效率或获得全局加成。查看升级面板获取强力提升！',
    icon: '📈',
    target: 'tab-upgrades',
    position: 'bottom',
  },
  {
    id: 'prestige',
    title: '⭐ 转生系统',
    content: '当能量达到100万时，可以转生获得永恒点数，大幅提升所有产出！',
    icon: '✨',
    target: 'tab-prestige',
    position: 'bottom',
  },
  {
    id: 'quests',
    title: '📋 任务系统',
    content: '完成任务获得奖励！每日任务重置，坚持签到获取额外加成。',
    icon: '🎯',
    target: 'tab-quests',
    position: 'bottom',
  },
  {
    id: 'complete',
    title: '🚀 你准备好了！',
    content: '开始你的宇宙征服之旅！点击太阳，建设帝国，成为宇宙帝王！',
    icon: '👑',
    target: 'clickArea',
    position: 'center',
  },
];

export default function Tutorial() {
  const [currentStep, setCurrentStep] = useState(0);
  const [completed, setCompleted] = useState(false);
  const [showTutorial, setShowTutorial] = useState(false);

  useEffect(() => {
    // Check if tutorial has been completed before
    const tutorialDone = localStorage.getItem('starforge_tutorial_done');
    if (tutorialDone === 'true') {
      setCompleted(true);
      return;
    }

    // Show tutorial after a short delay
    const timer = setTimeout(() => {
      setShowTutorial(true);
    }, 1500);

    return () => clearTimeout(timer);
  }, []);

  const nextStep = () => {
    if (currentStep < TUTORIAL_STEPS.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      completeTutorial();
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const skipTutorial = () => {
    completeTutorial();
  };

  const completeTutorial = () => {
    localStorage.setItem('starforge_tutorial_done', 'true');
    setCompleted(true);
  };

  if (completed || !showTutorial) return null;

  const step = TUTORIAL_STEPS[currentStep];
  const isFirst = currentStep === 0;
  const isLast = currentStep === TUTORIAL_STEPS.length - 1;

  return (
    <div className={styles.overlay}>
      <div className={styles.tutorial} data-position={step.position}>
        <div className={styles.content}>
          <div className={styles.icon}>{step.icon}</div>
          <h3 className={styles.title}>{step.title}</h3>
          <p className={styles.text}>{step.content}</p>
          
          <div className={styles.progress}>
            {TUTORIAL_STEPS.map((_, index) => (
              <div 
                key={index} 
                className={`${styles.dot} ${index === currentStep ? styles.active : ''} ${index < currentStep ? styles.completed : ''}`}
              />
            ))}
          </div>

          <div className={styles.buttons}>
            {!isFirst && (
              <button className={styles.btnSecondary} onClick={prevStep}>
                ← 上一步
              </button>
            )}
            <button className={styles.btnSkip} onClick={skipTutorial}>
              跳过
            </button>
            <button className={styles.btnPrimary} onClick={nextStep}>
              {isLast ? '开始游戏！' : '下一步 →'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
