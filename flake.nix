{
  description = "PyTorch with CUDA";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      # Supported systems
      supportedSystems = [ "x86_64-linux" "aarch64-linux" ];

      # Helper function to generate outputs for each system
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;

      # Import nixpkgs for each system
      pkgsFor = system: import nixpkgs {
        inherit system;
        config.allowUnfree = true;
      };
    in
    {
      devShells = forAllSystems (system:
        let
          pkgs = pkgsFor system;
        in
        {
          default = pkgs.mkShell {
            LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
              pkgs.stdenv.cc.cc
              pkgs.zlib
              pkgs.libGL
              pkgs.glib
              "/run/opengl-driver"
            ];

            venvDir = ".venv";
            packages = with pkgs; [
              python312
              python312Packages.venvShellHook
              python312Packages.pip
              uv
              figlet
            ];

            shellHook = ''
              figlet RAG env

              if [ ! -d ".venv" ]; then
                uv venv .venv
              fi

              source .venv/bin/activate

              # alias pip="uv pip"

              uv pip install -r requirements.txt

              figlet RAG started
            '';
          };
        }
      );
    };
}

