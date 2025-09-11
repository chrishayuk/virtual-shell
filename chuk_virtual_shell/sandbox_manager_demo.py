from chuk_virtual_shell.sandbox_manager import SandboxManager


def demo():
    # Create a SandboxManager
    mgr = SandboxManager()

    # 1) Start a new sandbox with the default memory provider
    session_id = mgr.start_sandbox()

    print("Session ID:", session_id)

    # 2) Join the sandbox by session ID
    mgr.join_sandbox(session_id)

    # 3) Write a file into the sandbox
    mgr.write_file(session_id, "/test.txt", "Hello from the sandbox!")

    # 4) Read (download) a file from the sandbox
    contents = mgr.download_file(session_id, "/test.txt")
    print("Sandbox file contents:", contents)

    # 5) Install a Python package inside the sandbox (demo)
    mgr.install_package(session_id, "requests")

    # 6) Stop the sandbox
    mgr.stop_sandbox(session_id)


if __name__ == "__main__":
    demo()
