# Portfolio visual provenance

Generated 2026-09-22. Figures are original visualisations, with sources identified
in source-manifest.json. Source repositories were read only, not modified.

- **dephasing.svg**: executed original bloch_sim.py, T=10, dt=0.01,
  omega=3, gamma_phi=0.12; free and Hahn echo at t=5. Verified transverse
  magnitude equals exp(-gamma_phi*t). Pulses refocus phase, not Markovian decay.
  The original run_benchmark.py also completed successfully.
- **integration.svg**: executed original integration_methods.py with the Agg
  backend. Restyled its returned sample-count and integral-estimate arrays.
  Sample counts are 2 through 51. The infinite-domain analytical limit is sqrt(pi);
  the numerical domain is [-5,5]. Original script emits harmless escape warnings.
- **majorization.svg**: reviewed and executed function definitions from cells
  2–5 of the 51 MB T_parameter_finder.ipynb in the state-transfer repository.
  Demonstrated [6,3,1] -> [5,4,1] -> [5,3,2], both mixing parameters 2/3.
  Checked conservation of total weight and the final vector; chart divides by 10.
  This validates one example, not every notebook cell or the full quantum protocol.
- **traxis.svg**: executed the unmodified fitCircle routine with lightweight
  marker-shaped inputs instead of Qt objects. Synthetic circle centre (2,-1),
  radius 4; Gaussian coordinate noise sigma=0.045, seed 17, 30 points.
  Fitted radius 4.0499559. This is not experimental data or a full GUI run.
  Traxis is collaborative software; the fitter credits the original developers.
- **robotics.svg**: explanatory architecture based on robot_arduino_program.ino
  and robot_pic_program.c. Firmware was not run: physical devices, PIC toolchain,
  and referenced support headers are not supplied in the repository.
- **notes.svg**: new free-particle illustration of Hamilton's principle,
  informed by page 2 of Lagrangian_Lecture_Notes.pdf. The notes' second PDF,
  Position_Momentum_Notes.pdf, was also read. These are PDF reading resources,
  not a runnable software repository; no claims about planned README topics.
- **graphene.svg**: original plot of the report's analytic dispersion,
  E/t = +/-sqrt(3+f(k)), t'=0 and a=1, around a Dirac point.
  Not a new Quantum ESPRESSO run or a reproduction of its DFT results.
  The report's conclusion identifies defect-state calculations as future work.

Numerical outputs and checks are in verification.json. To regenerate, install
numpy/scipy/matplotlib and arrange public source checkouts under one folder with
their GitHub repository names. Copy the state-transfer notebook to
SOURCE_ROOT/majorization.ipynb, then run:

    python generate_visuals.py SOURCE_ROOT

The script also creates local PNG previews for inspection; published figures use
SVG for sharp rendering. The thesis code remains private and was not executed.
