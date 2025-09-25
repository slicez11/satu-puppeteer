"use client";

import { useState } from "react";

export default function HomePage() {
  const [url, setUrl] = useState("https://satu.unri.ac.id");
  const [username, setUsername] = useState(
    "hussein.al.muhtadeebillah@lecturer.unri.ac.id"
  );
  const [password, setPassword] = useState("");
  const [screenshot, setScreenshot] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [elementSelectors, setElementSelectors] = useState<{
    emailSelector: string | null;
    passwordSelector: string | null;
    continueSelector: string | null;
    loginSelector: string | null;
    loginStatus: string | null;
  } | null>(null);

  const handleLoginScreenshot = async () => {
    if (!password) {
      setError("Please enter your password.");
      return;
    }

    setLoading(true);
    setError(null);
    setScreenshot(null);
    setElementSelectors(null);

    try {
      const response = await fetch("/api/login-screenshot", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username,
          password,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || "Login failed");
      }

      // Extract element selectors from headers
      const selectors = {
        emailSelector: response.headers.get("X-Email-Selector"),
        passwordSelector: response.headers.get("X-Password-Selector"),
        continueSelector: response.headers.get("X-Continue-Selector"),
        loginSelector: response.headers.get("X-Login-Selector"),
        loginStatus: response.headers.get("X-Login-Status"),
      };
      setElementSelectors(selectors);

      const blob = await response.blob();
      setScreenshot(URL.createObjectURL(blob));
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "An unknown error occurred."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gray-50">
      <div className="w-full max-w-2xl text-center">
        <h1 className="text-4xl font-bold mb-4 text-gray-800">
          SATU Login Screenshot
        </h1>
        <p className="text-lg text-gray-600 mb-8">
          Login to SATU and capture dashboard screenshot with element selectors.
        </p>

        <div className="space-y-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              URL
            </label>
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-black focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Username
            </label>
            <input
              type="email"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-black focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-black focus:outline-none"
            />
          </div>
        </div>

        <button
          onClick={handleLoginScreenshot}
          disabled={loading}
          className="w-full px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
        >
          {loading ? "Logging in..." : "Login & Capture Screenshot"}
        </button>
        {error && <p className="text-red-500 mt-4">{error}</p>}

        {elementSelectors && (
          <div className="mt-6 p-4 bg-gray-100 rounded-lg text-left">
            <h3 className="text-lg font-semibold mb-3 text-gray-800">
              Element Selectors Found:
            </h3>
            <div className="space-y-2 text-sm">
              <div>
                <strong>Email Selector:</strong>{" "}
                <code className="bg-gray-200 px-2 py-1 rounded">
                  {elementSelectors.emailSelector}
                </code>
              </div>
              <div>
                <strong>Password Selector:</strong>{" "}
                <code className="bg-gray-200 px-2 py-1 rounded">
                  {elementSelectors.passwordSelector}
                </code>
              </div>
              <div>
                <strong>Continue Selector:</strong>{" "}
                <code className="bg-gray-200 px-2 py-1 rounded">
                  {elementSelectors.continueSelector}
                </code>
              </div>
              <div>
                <strong>Login Selector:</strong>{" "}
                <code className="bg-gray-200 px-2 py-1 rounded">
                  {elementSelectors.loginSelector}
                </code>
              </div>
              <div>
                <strong>Status:</strong>{" "}
                <span className="text-green-600 font-semibold">
                  {elementSelectors.loginStatus}
                </span>
              </div>
            </div>
          </div>
        )}

        {screenshot && (
          <div className="mt-8 border border-gray-200 rounded-lg shadow-lg overflow-hidden">
            <h2 className="text-2xl font-semibold p-4 bg-gray-100 border-b text-black">
              Dashboard Screenshot
            </h2>
            <img
              src={screenshot || "/placeholder.svg"}
              alt="Dashboard screenshot"
              className="w-full"
            />
          </div>
        )}
      </div>
    </main>
  );
}
