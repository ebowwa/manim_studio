#!/bin/bash

# Add LaTeX to PATH
echo 'export PATH="/Library/TeX/texbin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Verify latex installation
which latex
which tlmgr
