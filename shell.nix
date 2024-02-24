let pkgs = import <nixpkgs> { };
in pkgs.mkShell {

  buildInputs = with pkgs; [
    python312
    python312Packages.pypandoc
    #
    uv # Add uv to the build inputs
    stdenv.cc.cc
    zlib
    fuse3
    # icu
    # nss
    # openssl
    # curl
    figlet
    # expat
    # xorg.libX11
    # vulkan-headers
    # vulkan-loader
    # vulkan-tools
    imagemagick
    texliveBasic
    texliveSmall
    texliveMedium
    texliveTeTeX
  ];

  packages = with pkgs;
    [
      # figlet
      # python3
      # gcc
      # grpc
      # python312Packages.qdrant-client
      # libstdcxx5
      # python311Packages.pip
    ];

  shellHook = ''
            export LD_LIBRARY_PATH=${
              pkgs.lib.makeLibraryPath [
                pkgs.stdenv.cc.cc
                pkgs.zlib
                pkgs.libGL
                pkgs.glib
                pkgs.fuse3
                pkgs.icu
                pkgs.nss
                pkgs.openssl
                pkgs.curl
                pkgs.expat
                pkgs.xorg.libX11
                pkgs.vulkan-headers
                pkgs.vulkan-loader
                pkgs.vulkan-tools
              ]
            }:$LD_LIBRARY_PATH

    		figlet RattaAI 

        if [ ! -d ".venv" ]; then
          uv venv .venv
        fi
    		
        # python -m venv .venv

    		source .venv/bin/activate
    		
        alias pip="uv pip"
        
        uv pip install -r requirements.txt

        
        # nix shell github:GuillaumeDesforges/fix-python
        # fix-python --venv .venv --libs .nix/libs.nix
        
        figlet RattaAI
  '';
}
