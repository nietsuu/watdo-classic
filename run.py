if __name__ == "__main__":
    import sys
    from watdo import main
    from watdo.entry_point import main_wrapper

    try:
        sys.exit(main_wrapper(main))
    except KeyboardInterrupt:
        sys.exit(130)
