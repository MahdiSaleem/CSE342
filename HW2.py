import socket
import os

def run_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 8080))
    server.listen(5)
    server.settimeout(30)  # Set timeout for accepting connections
    print("Server is listening on port 8080...")
    return server

def handle_request(client_socket, request):
    if not request.strip():  # Check if request is empty or only contains whitespace
        print("Received an empty request.")
        response = "HTTP/1.1 400 Bad Request\nContent-Type: text/html\n\n<h1>400 Bad Request</h1>"
        client_socket.sendall(response.encode())
        client_socket.close()
        return
    
    try:
        request_line = request.splitlines()[0]
        method, url, _ = request_line.split(" ")
        print(f"Method: {method}, URL: {url}")

        # Serve the requested file or return 404
        if url == "/":
            url = "/index.html"
        full_path = os.path.join("static", url.strip("/"))

        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8") as file:
                content = file.read()
            content = content.replace("{{METHOD}}", method).replace("{{URL}}", url).replace("{{STATUS_CODE}}", "200 OK")
            response = f"HTTP/1.1 200 OK\nContent-Type: text/html\n\n{content}"
            status_code = "200 OK"
        else:
            response = "HTTP/1.1 404 Not Found\nContent-Type: text/html\n\n<h1>404 File Not Found</h1>"
            status_code = "404 Not Found"
        
        print(f"Status: {status_code}")
        client_socket.sendall(response.encode())
    
    except Exception as e:
        print(f"Error handling request: {e}")
        error_response = "HTTP/1.1 500 Internal Server Error\nContent-Type: text/html\n\n<h1>500 Internal Server Error</h1>"
        client_socket.sendall(error_response.encode())
    
    finally:
        client_socket.close()

def handle_requests(server):
    while True:
        try:
            client_socket, _ = server.accept()
            client_socket.settimeout(30)  # Set timeout for receiving data
            request = client_socket.recv(1024).decode('utf-8')
            if request:
                handle_request(client_socket, request)
            else:
                print("Received an empty request.")
                response = "HTTP/1.1 400 Bad Request\nContent-Type: text/html\n\n<h1>400 Bad Request</h1>"
                client_socket.sendall(response.encode())
                client_socket.close()
        except socket.timeout:
            print("Client connection timed out.")
        except Exception as e:
            print(f"Error accepting connection: {e}")

server = run_server()
handle_requests(server)
