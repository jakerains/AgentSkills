import Foundation

final class WebSocketBridge {
    private let task: URLSessionWebSocketTask

    init(url: URL, bearerToken: String? = nil) {
        let configuration = URLSessionConfiguration.default
        let session = URLSession(configuration: configuration)

        var request = URLRequest(url: url)
        if let bearerToken {
            request.setValue("Bearer \(bearerToken)", forHTTPHeaderField: "Authorization")
        }

        self.task = session.webSocketTask(with: request)
    }

    func connect() {
        task.resume()
    }

    func sendInitialize() async throws {
        let payload: [String: Any] = [
            "id": 1,
            "method": "initialize",
            "params": [
                "clientInfo": [
                    "name": "my_swift_host",
                    "title": "My Swift Host",
                    "version": "0.1.0"
                ],
                "capabilities": [
                    "experimentalApi": true
                ]
            ]
        ]

        let data = try JSONSerialization.data(withJSONObject: payload)
        try await task.send(.string(String(decoding: data, as: UTF8.self)))
    }
}

// Use this pattern when the Swift host cannot spawn a local process.
// Keep the app-server listener authenticated and avoid exposing a non-loopback listener without explicit auth.
