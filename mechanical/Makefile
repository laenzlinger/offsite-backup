.DEFAULT_GOAL := help
.PHONY: assembly pcb-step clean help

PCB_DIR := ../hardware

pcb-step: ## Export PCB STEP from KiCad
	cd $(PCB_DIR) && kicad-cli pcb export step \
		--define-var GIT_HASH=$$(git rev-parse --short HEAD) \
		--output ../mechanical/granit-pcb.step \
		--subst-models --force granit.kicad_pcb

assembly: pcb-step ## Build FreeCAD assembly (STEP + FCStd)
	cd .. && freecadcmd mechanical/assembly.py

screenshot: assembly ## Render assembly screenshot
	cd .. && xvfb-run -a -s "-screen 0 1920x1080x24" freecad mechanical/screenshot.py

clean:
	rm -f granit-pcb.step assembly.step assembly.FCStd

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
