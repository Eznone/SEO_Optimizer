# Frontend Setup Guide

This project uses **Next.js** for the frontend, which communicates with the **Django** backend via a proxy.

## Prerequisites

- **Node.js** (v18.17 or later)
- **npm** or **yarn**
- **Running Backend:** The backend must be running at `http://127.0.0.1:8000` for the frontend to function correctly (auth and API proxying).

## Getting Started

1.  **Navigate to the frontend directory:**

    ```bash
    cd frontend
    ```

2.  **Install dependencies:**

    ```bash
    npm install
    ```

3.  **Run the development server:**

    ```bash
    npm run dev
    ```

4.  **Access the application:**
    Open [http://localhost:3000](http://localhost:3000) in your browser.

## Configuration

The frontend is configured to proxy requests to the backend. You can modify this in `next.config.ts`:

```typescript
const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://127.0.0.1:8000/api/:path*",
      },
      {
        source: "/accounts/:path*",
        destination: "http://127.0.0.1:8000/accounts/:path*",
      },
    ];
  },
};
```

## Production Build

To create a production-optimized build:

```bash
npm run build
npm start
```
