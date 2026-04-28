import re
with open("templates/base.html", "r") as f:
    content = f.read()

pattern = r"<footer class=\"bg-dark text-light py-3 mt-5\">.*?</footer>"
replacement = """<footer class=\"bg-dark text-light py-3 mt-5\">
        <div class=\"container-fluid\">
            <div class=\"row align-items-center\">
                <div class=\"col-md-4\">
                </div>
                <div class=\"col-md-4 text-center\">
                    <small>&copy; 2025 <a href=\"https://alkhudarigroup.com\" target=\"_blank\" style=\"color: var(--trading-yellow); text-decoration: none; font-weight: bold;\">Alkhudari Group</a>. All rights reserved.</small>
                </div>
                <div class=\"col-md-4 text-end d-flex justify-content-end align-items-center\">
                    <small>
                        <span id=\"connectionStatus\" class=\"connection-status text-success\">
                            <i class=\"fas fa-circle me-1\"></i>Connected
                        </span>
                    </small>
                </div>
            </div>
        </div>
    </footer>"""

new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
with open("templates/base.html", "w") as f:
    f.write(new_content)

print("Footer fixed!")
