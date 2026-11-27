const [major, minor, patch] = process.versions.node.split('.').map(Number);
if (major !== 24 || minor < 22 || (minor === 22 && patch < 3)) {
  console.error(`本課建置固定 Node.js 24.22.3 至 24.x；目前 ${process.versions.node}。請先安裝並切換到符合版本，再確認 node --version。只讀隨附產物可用 node serve-dist.js。`);
  process.exitCode = 1;
}
