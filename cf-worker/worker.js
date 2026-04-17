/**
 * Cloudflare Worker — HTTP Basic Auth 게이트
 * 환경변수: DASHBOARD_PASSWORD (Cloudflare 대시보드에서 설정)
 */
export default {
  async fetch(request, env) {
    const password = env.DASHBOARD_PASSWORD;

    const authHeader = request.headers.get("Authorization");
    if (authHeader && authHeader.startsWith("Basic ")) {
      const encoded = authHeader.slice(6);
      const decoded = atob(encoded);           // "user:password"
      const inputPw = decoded.split(":")[1];
      if (inputPw === password) {
        return fetch(request);                 // 인증 성공 → 원본 Pages로
      }
    }

    return new Response("Unauthorized", {
      status: 401,
      headers: {
        "WWW-Authenticate": 'Basic realm="Leading Stock Dashboard"',
        "Content-Type": "text/plain",
      },
    });
  },
};
