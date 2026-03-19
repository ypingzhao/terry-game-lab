const https = require('https');
const http = require('http');
const { parseString } = require('xml2js');
const fs = require('fs');
const url = require('url');

// 读取配置
const NEWS_SOURCES = JSON.parse(fs.readFileSync('./news-sources.json', 'utf8'))
  .filter(s => s.enabled);

console.log(`加载了 ${NEWS_SOURCES.length} 个启用的RSS源`);

const CORS_PROXIES = [
  'https://api.allorigins.win/raw?url=',
  'https://api.codetabs.com/v1/proxy?quest=',
];

function getCORSProxy() {
  return CORS_PROXIES[Math.floor(Math.random() * CORS_PROXIES.length)];
}

function fetchUrl(targetUrl) {
  return new Promise((resolve, reject) => {
    const proxyUrl = getCORSProxy() + encodeURIComponent(targetUrl);
    const parsedUrl = new URL(proxyUrl);
    
    const options = {
      hostname: parsedUrl.hostname,
      path: parsedUrl.pathname + parsedUrl.search,
      method: 'GET',
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; RSS fetcher)'
      },
      timeout: 15000
    };

    const requester = parsedUrl.protocol === 'https:' ? https : http;
    
    const req = requester.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => resolve(data));
    });
    
    req.on('error', reject);
    req.on('timeout', () => reject(new Error('timeout')));
    req.end();
  });
}

function parseRSS(xmlText, source) {
  return new Promise((resolve, reject) => {
    parseString(xmlText, (err, result) => {
      if (err) return reject(err);
      
      let items = [];
      if (result?.rss?.channel?.[0]?.item) {
        items = result.rss.channel[0].item;
      } else if (result?.feed?.entry) {
        items = result.feed.entry;
      }
      
      if (!items || items.length === 0) {
        return resolve([]);
      }
      
      const parsed = items.slice(0, 15).map(item => {
        const title = item.title?.[0]?._ || item.title?.[0] || '';
        let link = '';
        if (item.link?.[0]?.$?.href) {
          link = item.link[0].$.href;
        } else if (item.link?.[0]) {
          link = item.link[0];
        }
        let description = '';
        if (item.description?.[0]?._) {
          description = item.description[0]._;
        } else if (item.description?.[0]) {
          description = item.description[0];
        } else if (item.summary?.[0]) {
          description = item.summary[0];
        }
        let pubDate = '';
        if (item.pubDate?.[0]) {
          pubDate = item.pubDate[0];
        } else if (item.published?.[0]) {
          pubDate = item.published[0];
        } else if (item.updated?.[0]) {
          pubDate = item.updated[0];
        }
        
        let summary = description.replace(/<[^>]*>/g, '');
        if (summary.length > 200) {
          summary = summary.slice(0, 200) + '...';
        }
        
        return {
          title: title.trim(),
          link: link.trim(),
          summary: summary.trim(),
          time: new Date(pubDate).getTime(),
          source: source.name,
          categories: source.categories,
          sourceColor: source.color || 'rgba(0, 255, 255, 0.3)'
        };
      }).filter(item => item.title && item.link && !isNaN(item.time));
      
      resolve(parsed);
    });
  });
}

async function fetchSource(source) {
  try {
    console.log(`正在抓取: ${source.name} - ${source.url}`);
    const xml = await fetchUrl(source.url);
    const items = await parseRSS(xml, source);
    console.log(`  → 获取到 ${items.length} 条新闻`);
    return items;
  } catch (e) {
    console.error(`  → 抓取失败: ${e.message}`);
    return [];
  }
}

function mergeNews(existing, newNews) {
  const urlMap = new Map();
  
  // 添加已有新闻
  existing.forEach(n => urlMap.set(n.link, n));
  
  // 添加新新闻，去重
  newNews.forEach(n => urlMap.set(n.link, n));
  
  // 转回数组，按时间排序
  let merged = Array.from(urlMap.values());
  merged.sort((a, b) => b.time - a.time);
  
  // 只保留最近90天，最多200条
  const ninetyDaysAgo = Date.now() - 90 * 24 * 60 * 60 * 1000;
  merged = merged.filter(n => n.time > ninetyDaysAgo);
  
  if (merged.length > 200) {
    merged = merged.slice(0, 200);
  }
  
  return merged;
}

function generateNewsSummaryHtml(merged) {
  // 统计分类
  const categoryMap = {
    game: '新游发布',
    company: '公司动态',
    investment: '行业资本',
    industry: '行业动态',
    policy: '政策监管'
  };
  
  const counts = {
    game: 0,
    company: 0,
    investment: 0,
    industry: 0,
    policy: 0
  };
  
  merged.forEach(n => {
    n.categories.forEach(c => {
      if (counts[c] !== undefined) {
        counts[c]++;
      }
    });
  });
  
  // 获取热门标题（只保留游戏行业相关，取最近15条）
  const hotTitles = merged
    .slice(0, 15)
    .map(n => `<a href="${n.link}" target="_blank" rel="noopener">${n.title}</a>`)
    .join('</li>\n  <li>');
  
  const now = new Date().toLocaleString('zh-CN');
  
  return `
<!-- 新闻小结 START -->
<div class="news-summary">
  <div class="summary-card">
    <h3>📊 今日资讯小结</h3>
    <div class="summary-stats">
      <div class="stat-item">
        <span class="stat-number">${merged.length}</span>
        <span class="stat-label">总资讯</span>
      </div>
      <div class="stat-item">
        <span class="stat-number">${counts.game}</span>
        <span class="stat-label">新游发布</span>
      </div>
      <div class="stat-item">
        <span class="stat-number">${counts.investment}</span>
        <span class="stat-label">行业资本</span>
      </div>
      <div class="stat-item">
        <span class="stat-number">${counts.company}</span>
        <span class="stat-label">公司动态</span>
      </div>
    </div>
    <div class="hot-titles">
      <h4>🔥 最新热门</h4>
      <ul>
        <li>${hotTitles}</li>
      </ul>
    </div>
    <div class="last-update">最后更新：${now}</div>
  </div>
</div>
<!-- 新闻小结 END -->
`;
}

async function updateNewsHtmlWithSummary(merged) {
  try {
    // 读取现有的 news.html
    let htmlContent = fs.readFileSync('./news.html', 'utf8');
    
    // 检查是否已有小结，如果有则替换
    const summaryHtml = generateNewsSummaryHtml(merged);
    
    if (htmlContent.includes('<!-- 新闻小结 START -->')) {
      // 替换现有小结
      htmlContent = htmlContent.replace(
        /<!-- 新闻小结 START -->[\s\S]*<!-- 新闻小结 END -->/,
        summaryHtml
      );
    } else {
      // 在 filters 之前插入小结
      htmlContent = htmlContent.replace(
        /        <div class="filters">/,
        `${summaryHtml}\n        <div class="filters">`
      );
    }
    
    // 写回文件
    fs.writeFileSync('./news.html', htmlContent, 'utf8');
    console.log(`✅ 已更新 news.html，添加新闻小结 (${merged.length} 条新闻)`);
    return true;
  } catch (e) {
    console.error('❌ 更新 news.html 失败:', e.message);
    return false;
  }
}

async function main() {
  // 读取现有缓存
  let existing = [];
  if (fs.existsSync('./cached-news.json')) {
    try {
      existing = JSON.parse(fs.readFileSync('./cached-news.json', 'utf8'));
      console.log(`读取现有缓存: ${existing.length} 条新闻`);
    } catch (e) {
      console.log('无现有缓存，从头开始');
    }
  }
  
  // 抓取所有源
  const allResults = [];
  for (const source of NEWS_SOURCES) {
    const items = await fetchSource(source);
    allResults.push(...items);
    // 延时，避免被封
    await new Promise(r => setTimeout(r, 2000));
  }
  
  console.log(`\n总共抓取到 ${allResults.length} 条新闻`);
  
  // 合并去重
  const merged = mergeNews(existing, allResults);
  console.log(`合并去重后: ${merged.length} 条新闻`);
  
  // 保存
  fs.writeFileSync('./cached-news.json', JSON.stringify(merged, null, 2), 'utf8');
  console.log(`\n已保存到 cached-news.json，共 ${merged.length} 条`);
  
  // 更新 news.html 添加新闻小结
  await updateNewsHtmlWithSummary(merged);
  
  if (merged.length >= 100) {
    console.log('✓ 已达到100篇目标！');
  } else {
    console.log(`✗ 还差 ${100 - merged.length} 篇达到100篇`);
  }
}

main().catch(console.error);
