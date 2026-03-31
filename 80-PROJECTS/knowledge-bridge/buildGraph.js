/**
 * Knowledge Bridge - Build Initial Graph
 * "知识的六度分隔" - Cross-domain knowledge graph with analogies
 */

const { graph } = require('./knowledgeGraph');
const fs = require('fs');

// Create data directory
if (!fs.existsSync('data')) fs.mkdirSync('data');

const DOMAINS = {
  CHEMISTRY: 'chemistry',
  PROGRAMMING: 'programming',
  COOKING: 'cooking',
  MEDICINE: 'medicine',
  ENGINEERING: 'engineering'
};

// ===== STEP 1: CHEMISTRY CONCEPTS =====

const plaStructure = graph.addConcept('PLA结构', DOMAINS.CHEMISTRY,
  '聚乳酸(PLA)是聚酯的一种，由乳酸单体通过酯键连接成聚合物链');

const esterBond = graph.addConcept('酯键', DOMAINS.CHEMISTRY,
  'PLA中的官能团-COO-，能被水分子攻击导致断链');

const hydrolysis = graph.addConcept('水解降解', DOMAINS.CHEMISTRY,
  '水分子攻击酯键，使聚合物分子量下降的过程');

const microbial = graph.addConcept('微生物降解', DOMAINS.MEDICINE,
  '微生物分泌酶，将乳酸分解为CO2和H2O');

const firstOrder = graph.addConcept('一级反应动力学', DOMAINS.CHEMISTRY,
  'M(t) = M0 * e^(-kt)，分子量随时间指数下降');

const halfLife = graph.addConcept('半衰期', DOMAINS.CHEMISTRY,
  '分子量减少一半所需时间，t1/2 = ln(2)/k');

const tempEffect = graph.addConcept('温度效应', DOMAINS.CHEMISTRY,
  '温度升高加速水解反应，符合阿伦尼乌斯方程');

const mwDistribution = graph.addConcept('分子量分布', DOMAINS.CHEMISTRY,
  'PDI值越大，聚合物链长越不均匀');

const crystallinity = graph.addConcept('结晶度', DOMAINS.CHEMISTRY,
  '结晶区水解慢于无定形区，影响降解速率');

const mechanicalProps = graph.addConcept('机械性能', DOMAINS.ENGINEERING,
  '拉伸强度等性能指标，随降解下降');

// ===== STEP 2: PROGRAMMING CONCEPTS =====

const memoryLeak = graph.addConcept('内存泄漏', DOMAINS.PROGRAMMING,
  '程序运行中未释放的内存持续积累，导致可用内存减少');

const garbageCollection = graph.addConcept('垃圾回收', DOMAINS.PROGRAMMING,
  '自动识别和释放不再使用的内存的机制');

const microservices = graph.addConcept('微服务崩溃', DOMAINS.PROGRAMMING,
  '一个服务故障导致级联失败的现象');

const tryFinally = graph.addConcept('Try-Finally块', DOMAINS.PROGRAMMING,
  '确保无论是否异常，finally代码块都会执行');

const cpuFreq = graph.addConcept('CPU频率调节', DOMAINS.PROGRAMMING,
  '处理器根据负载动态调整频率的机制');

const deprecation = graph.addConcept('API弃用', DOMAINS.PROGRAMMING,
  '旧版API宣布过时，最终将被移除');

const techDebt = graph.addConcept('技术债务', DOMAINS.PROGRAMMING,
  '快速开发积累的低质量代码，后期维护成本高');

const codeReview = graph.addConcept('代码审查', DOMAINS.PROGRAMMING,
  '团队检查代码质量和一致性的过程');

// ===== STEP 3: COOKING CONCEPTS =====

const cookingMeat = graph.addConcept('炖肉软烂', DOMAINS.COOKING,
  '长时间高温加热使肉类蛋白质分解、结构松散');

const foodDecomposition = graph.addConcept('食物腐败', DOMAINS.COOKING,
  '微生物作用下食物变质分解');

// ===== STEP 4: MEDICINE CONCEPTS =====

const drugMetabolism = graph.addConcept('药物代谢', DOMAINS.MEDICINE,
  '药物在体内被酶分解成代谢物的过程');

const enzymeActivity = graph.addConcept('酶活性', DOMAINS.MEDICINE,
  '酶催化反应的效率，受温度和pH影响');

const halfLifeMedicine = graph.addConcept('药物半衰期', DOMAINS.MEDICINE,
  '药物浓度减少一半所需时间');

// ===== STEP 5: CONNECTIONS (Intra-domain) =====

// Chemistry
graph.connect(plaStructure, esterBond, 'contains', 1);
graph.connect(esterBond, hydrolysis, 'enables', 1);
graph.connect(hydrolysis, microbial, 'feeds', 1);
graph.connect(firstOrder, halfLife, 'defines', 1);
graph.connect(hydrolysis, firstOrder, 'follows', 1);
graph.connect(tempEffect, hydrolysis, 'accelerates', 1);
graph.connect(mwDistribution, mechanicalProps, 'determines', 1);
graph.connect(crystallinity, hydrolysis, 'modulates', 1);
graph.connect(mechanicalProps, hydrolysis, 'decreases_during', 1);

// Programming
graph.connect(memoryLeak, garbageCollection, 'needs', 1);
graph.connect(tryFinally, garbageCollection, 'relates_to', 1);
graph.connect(deprecation, techDebt, 'creates', 1);

// Medicine
graph.connect(drugMetabolism, enzymeActivity, 'depends_on', 1);
graph.connect(drugMetabolism, microbial, 'similar_to', 1);
graph.connect(halfLifeMedicine, halfLife, 'similar_to', 1);
graph.connect(enzymeActivity, tempEffect, 'similar_to', 1);

// Cooking
graph.connect(cookingMeat, tempEffect, 'similar_to', 1);
graph.connect(cookingMeat, foodDecomposition, 'relates_to', 1);

// ===== STEP 6: CROSS-DOMAIN ANALOGIES =====

// 1. Hydrolysis ≈ Memory leak
graph.addAnalogy(hydrolysis, memoryLeak,
  'PLA水解就像内存泄漏：系统（聚合物）持续产生需要清理的东西（短链），但没有垃圾回收（微生物）时，内存（分子量）最终耗尽崩溃。');

// 2. Microbial degradation ≈ finally block
graph.addAnalogy(microbial, tryFinally,
  'PLA最终被微生物完全分解成CO2和H2O，就像try-catch-finally中的finally块——无论什么情况，finally都会执行，确保清理完成。');

// 3. Ester bond cleavage ≈ Microservices cascade failure
graph.addAnalogy(esterBond, microservices,
  '酯键被水切断就像微服务级联崩溃——一个关键服务宕了，依赖它的其他服务也会陆续崩溃（分子链断裂传导）。');

// 4. First-order kinetics ≈ CPU frequency scaling
graph.addAnalogy(firstOrder, cpuFreq,
  '一级反应动力学中，降解速率与当前浓度成正比——就像CPU降频：负载（浓度）越高，功耗（反应速率）越大，但效率不变。');

// 5. Half-life ≈ API deprecation
graph.addAnalogy(halfLife, deprecation,
  '半衰期是PLA分子量减少一半的时间，就像软件API的弃用周期：到了弃用日期，功能（分子量）减半，再过一个周期，彻底消失。');

// 6. Temperature effect ≈ Compilation speed
graph.addAnalogy(tempEffect, cookingMeat,
  '温度升高加速水解，就像炖肉——温度越高，肉（聚合物）软烂（降解）越快。');

// 7. PDI ≈ Code review inequality
graph.addAnalogy(mwDistribution, codeReview,
  'PDI大说明分子量分布不均匀，就像代码审查——有些代码质量很高（大分子），有些很烂（小分子），团队（材料）整体质量取决于最弱的那部分。');

// 8. Crystallinity ≈ Tech debt
graph.addAnalogy(crystallinity, techDebt,
  '结晶区降解慢就像技术债务——硬的部分（结晶区）很难处理，需要更多时间（高温/强酶）才能降解，但一旦开始，速度会加快。');

// 9. Mechanical decline ≈ Team productivity
graph.addAnalogy(mechanicalProps, drugMetabolism,
  '机械性能下降比分子量快，就像药物代谢——只要关键代谢物（长链）减少，疗效（强度）就会急剧下降，即使前体（短链）还在。');

// ===== SAVE =====

const savedPath = graph.save('pla-knowledge-graph.json');
console.log('\n=== Knowledge Graph Built ===\n');
console.log(`Total concepts: ${graph.nodes.size}`);
console.log(`Total connections: ${graph.edges.length}`);
console.log(`Total analogies: ${graph.analogyBank.length}`);
console.log(`Domains: ${[...graph.domains].join(', ')}`);
console.log(`\nSaved to: ${savedPath}`);

// Print analogy summary
console.log('\n=== Cross-Domain Analogies ===\n');
graph.analogyBank.forEach((a, i) => {
  const sourceNode = graph.nodes.get(a.source);
  const targetNode = graph.nodes.get(a.target);
  if (sourceNode && targetNode) {
    console.log(`${i + 1}. ${sourceNode.label} (${sourceNode.domain}) ≈ ${targetNode.label} (${targetNode.domain})`);
    console.log(`   "${a.text.substring(0, 80)}..."\n`);
  }
});

console.log('=== Ready for visualization ===');
console.log('Run: node visualize.js');
