import importlib.util
import os
import sys

os.environ["SSL_CERT_FILE"] = "/etc/ssl/cert.pem"
sys.path[:0] = ["/Users/gopalpatwa/opt/aveto-support/.claude/worktrees/interesting-shannon-67bff6"]
spec = importlib.util.spec_from_file_location("live", "/Users/gopalpatwa/opt/aveto-support/.claude/worktrees/interesting-shannon-67bff6/runs/polished-chat-experience/13-live/live.py")
m = importlib.util.module_from_spec(spec); sys.modules["live"] = m; spec.loader.exec_module(m)
raise SystemExit(m.main(sys.argv[1:]))
