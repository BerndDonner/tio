{
  description = "tio development shell";

  inputs = {
    nixos-config.url = "github:BerndDonner/NixOS-Config";
    nixpkgs.follows = "nixos-config/nixpkgs";
  };

  outputs = { self, nixpkgs, nixos-config, ... }:
    let
      system = "x86_64-linux";

      pkgs = import nixpkgs {
        inherit system;
        config.allowUnfree = true;
        overlays = [
          nixos-config.overlays.unstable
          nixos-config.overlays.pygame-avx2
        ];
      };

      cDev = import (nixos-config + "/lib/c-develop.nix");
    in
    {
      devShells.${system}.default = cDev {
        inherit pkgs;

        inputs = { inherit nixos-config nixpkgs; };
        checkInputs = [ "nixos-config" ];
        flakeLockPath = ./flake.lock;

        symbol = "";

        # tio defaults to LuaJIT in yabu76/develop_this_fork, but keeping
        # regular Lua available makes it easy to exercise both code paths.
        extraBuildInputs = with pkgs; [
          glib
          luajit
          lua5_4
          bash-completion
        ];

        extraPackages = with pkgs; [
          python3
          valgrind
          strace
          socat
        ];

        extraShellHook = ''
          export TIO_BUILD_DIR="$PWD/build"
          export PYTHONDONTWRITEBYTECODE=1

          tio-configure() {
            if [ -f "$TIO_BUILD_DIR/build.ninja" ]; then
              meson setup --reconfigure "$TIO_BUILD_DIR" -Duse_luajit=true "$@"
            else
              meson setup "$TIO_BUILD_DIR" -Duse_luajit=true "$@"
            fi
          }

          tio-build() {
            if [ ! -f "$TIO_BUILD_DIR/build.ninja" ]; then
              tio-configure || return
            fi
            meson compile -C "$TIO_BUILD_DIR" "$@"
          }

          tio-test() {
            tio-build || return
            meson test -C "$TIO_BUILD_DIR" --print-errorlogs "$@"
          }

          tio-e2e() {
            tio-build || return
            python3 tests/e2e_test.py "$TIO_BUILD_DIR/src/tio" --verbose "$@"
          }

          tio-check() {
            tio-test
          }

          echo
          echo "  tio-configure   configure/reconfigure build/ with LuaJIT"
          echo "  tio-build       compile tio"
          echo "  tio-test        run Meson-registered tests"
          echo "  tio-e2e         run yabu76's Python PTY end-to-end tests"
          echo "  tio-check       build + both test suites"
        '';

        message = " tio development shell ready";
      };
    };
}
