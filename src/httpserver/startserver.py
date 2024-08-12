import http.server
import socketserver
import os
from urllib.parse import unquote
import webbrowser

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Decode the path to handle spaces and special characters
        self.path = unquote(self.path)

        # Ensure the path is correctly formatted
        path = self.path.lstrip('/')
        
        # Handle directory requests
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                self.send_response(301)
                self.send_header('Location', self.path + '/')
                self.end_headers()
                return
            
            # Check for index.html
            index_path = os.path.join(path, 'index.html')
            if os.path.isfile(index_path):
                self.path = os.path.join(self.path, 'index.html')
                path = self.path.lstrip('/')
                super().do_GET()
                return
            
            # List directory contents if no index.html
            self.list_directory(path)
            return

        # Append '.html' if needed
        if not os.path.exists(path) and not self.path.endswith('.html'):
            self.path += '.html'
            path = self.path.lstrip('/')

        # Serve the file or custom 404 page
        if os.path.exists(path):
            super().do_GET()
        else:
            self.send_error(404)

    def list_directory(self, path):
        """List the contents of a directory with custom HTML and CSS."""
        try:
            abs_path = os.path.abspath(path)
            # Ensure the path is within the current working directory
            if not abs_path.startswith(os.getcwd()):
                self.send_error(403, "Forbidden")
                return

            files = os.listdir(path)
        except OSError as e:
            self.send_error(403, f"Forbidden: {e}")
            return

        files.sort()
        display_path = self.path

        # Prepare HTML response with inline CSS
        response = []
        response.append('<!DOCTYPE html>')
        response.append('<html lang="en">')
        response.append('<head>')
        response.append('<meta charset="UTF-8">')
        response.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
        response.append(f'<title>Directory listing for {display_path}</title>')
        response.append('<style>')
        response.append('body {')
        response.append('    margin: 0;')
        response.append('    padding: 0;')
        response.append('    font-family: system-ui, -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, Oxygen, Ubuntu, Cantarell, \'Open Sans\', \'Helvetica Neue\', sans-serif;')
        response.append('    background-color: #121212;')
        response.append('    color: #f0f0f0;')
        response.append('}')
        response.append('')
        response.append('.directory-listing {')
        response.append('    background-color: #1e1e1e;')
        response.append('    border-radius: 10px;')
        response.append('    padding: 20px;')
        response.append('    max-width: 800px;')
        response.append('    margin: 20px auto;')
        response.append('    color: white;')
        response.append('}')
        response.append('')
        response.append('.directory-listing h2 {')
        response.append('    color: #76B9ED;')
        response.append('}')
        response.append('')
        response.append('.directory-listing ul {')
        response.append('    list-style-type: none;')
        response.append('    padding: 0;')
        response.append('}')
        response.append('')
        response.append('.directory-listing li {')
        response.append('    margin: 5px 0;')
        response.append('}')
        response.append('')
        response.append('.directory-listing a.directory-item {')
        response.append('    color: #76B9ED;')
        response.append('    text-decoration: none;')
        response.append('    transition: color 0.3s;')
        response.append('}')
        response.append('')
        response.append('.directory-listing a.directory-item:hover {')
        response.append('    color: #5a9bd4;')
        response.append('    text-decoration: underline;')
        response.append('}')
        response.append('')
        response.append('.directory-listing hr {')
        response.append('    border: 1px solid #888;')
        response.append('    margin: 10px 0;')
        response.append('}')
        response.append('</style>')
        response.append('</head>')
        response.append('<body>')
        response.append('<div class="directory-listing">')
        response.append(f'<h2>Directory listing for {display_path}</h2>')
        response.append('<hr>')
        response.append('<ul>')

        # Parent directory link
        parent_dir = os.path.dirname(display_path)
        if parent_dir and parent_dir != display_path:
            response.append('<li><a class="directory-item" href="../">.. (Parent Directory)</a></li>')

        # Directory contents
        for name in files:
            full_path = os.path.join(path, name)
            display_name = name
            if os.path.isdir(full_path):
                display_name += '/'
            response.append(f'<li><a class="directory-item" href="{display_name}">{display_name}</a></li>')

        response.append('</ul>')
        response.append('<hr>')
        response.append('</div>')
        response.append('</body>')
        response.append('</html>')

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write('\n'.join(response).encode('utf-8'))

    def send_error(self, code, message=None):
        """Send an error response with a custom 404 page or default message."""
        if code == 404:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            
            # Read and send the custom 404.html file
            try:
                with open('dl404.html', 'r', encoding='utf-8') as file:
                    content = file.read()
                self.wfile.write(content.encode('utf-8'))
            except IOError:
                # Fallback if the 404.html file is not found
                self.send_response(500)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                response = '<!DOCTYPE html><html><body><h1>500 Internal Server Error</h1></body></html>'
                self.wfile.write(response.encode('utf-8'))
        else:
            super().send_error(code, message)

PORT = 5500

Handler = CustomHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    webbrowser.open('http://localhost:5500/index.html')
    print(f"Serving HTTP on port {PORT} (http://localhost:{PORT})...")
    httpd.serve_forever()