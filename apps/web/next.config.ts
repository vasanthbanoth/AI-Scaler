import type { NextConfig } from "next";
import path from "path";
import { config } from "dotenv";

// Load root .env so API routes get OPENAI_API_KEY + API_BASE_URL
config({ path: path.resolve(__dirname, "../../.env") });

const nextConfig: NextConfig = {
  reactStrictMode: true,
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "avatars.githubusercontent.com" },
      { protocol: "https", hostname: "images.unsplash.com" },
    ],
  },
};

export default nextConfig;
