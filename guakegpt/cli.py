from guakegpt.app import GuakeGPT

def main():
    print("Starting GuakeGPT...")
    app = GuakeGPT()
    try:
        print("Press F12 to show/hide the window")
        app.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
        app.quit()
    except Exception as e:
        print(f"Error: {e}")
        app.quit()

if __name__ == "__main__":
    main() 