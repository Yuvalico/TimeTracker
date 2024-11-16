to run backend:
    - verify anaconda installed
    - conda env create -f tw.yml
    - conda activate tw
    - change to backend directory
    - enter command "python main.py"

to compile backend:
    - run "nuitka --standalone --output-filename=backend  main.py "