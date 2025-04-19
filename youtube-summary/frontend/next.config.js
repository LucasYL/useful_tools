/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*', // Proxy to Backend
      },
    ];
  },
  // 增加API请求超时和响应大小限制
  api: {
    bodyParser: {
      sizeLimit: '10mb', // 增加请求体积限制
    },
    responseLimit: '10mb', // 增加响应体积限制
  },
  // 增加超时时间设置
  serverRuntimeConfig: {
    // 注意：此设置在某些版本可能不生效，取决于Next.js版本
    timeout: 120000, // 120秒
  },
};

module.exports = nextConfig; 