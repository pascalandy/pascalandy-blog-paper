Yeah, I think it would be nice to execute these tests and order them as a CI would do, but instead of having, but instead of running the commands on the OS Ubuntu, We're running it using an headless LLM. 


````yml
  build:
    name: Build (${{ matrix.name }})
    runs-on: ${{ matrix.os }}
    timeout-minutes: 30
    needs: check
    strategy:
      fail-fast: false
      matrix:
        include:
          # Linux x64 (glibc)
          - os: ubuntu-latest
            target: x86_64-unknown-linux-gnu
            name: linux-x64
          # Linux ARM64 (native runner - 10x faster than QEMU)
          - os: ubuntu-24.04-arm
            target: aarch64-unknown-linux-gnu
            name: linux-arm64
          # macOS Apple Silicon (native)
          - os: macos-14
            target: aarch64-apple-darwin
            name: macos-arm64
          # macOS Intel
          - os: macos-15
            target: x86_64-apple-darwin
            name: macos-x64
          # Windows x64
          - os: windows-latest
            target: x86_64-pc-windows-msvc
            name: windows-x64
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2

      - name: Install Rust toolchain
        uses: dtolnay/rust-toolchain@master
        with:
          toolchain: nightly
          targets: ${{ matrix.target }}

      - name: Cache cargo
        uses: Swatinem/rust-cache@ad397744b0d591a723ab90405b7247fac0e6b8db  # v2
        with:
          key: ${{ runner.os }}-${{ runner.arch }}-${{ matrix.target }}

      - name: Build release binary
        run: cargo build --release --target ${{ matrix.target }}

      - name: Verify binary runs (Unix)
        if: runner.os != 'Windows'
        run: ./target/${{ matrix.target }}/release/br --version

      - name: Verify binary runs (Windows)
        if: runner.os == 'Windows'
        run: ./target/${{ matrix.target }}/release/br.exe --version

      - name: Upload artifact (Unix)
        if: runner.os != 'Windows'
        uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02  # v4
        with:
          name: br-${{ matrix.name }}
          path: target/${{ matrix.target }}/release/br

      - name: Upload artifact (Windows)
        if: runner.os == 'Windows'
        uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02  # v4
        with:
          name: br-${{ matrix.name }}
          path: target/${{ matrix.target }}/release/br.exe
````