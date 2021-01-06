# NEAT_flappy_bird

 An AI that plays flappy bird using the NEAT python module.

## Getting Started
### Prerequisites

You need to install the following packages with pip:
* pygame
* neat

### Running "NEAT_flappy_bird"

Simply run flappy_bird.py

## How the Neat Algorithm works (in construction)
Input layer:
Bird y
Distance from top pipe
Distance from bottom pipe

Output :Jump or not

Activation function: Tan h

population : The bigger, the msot variation you will have
Fitness function : how far the bird went. We keep birds with the max fitness
Mex generations : when we cut the progam


NEAT favored basic neural networks

We repeat the process till we are happy about the performances of the bird.

## Resources I recommend on the subject

* [Original Neat Paper](http://nn.cs.utexas.edu/downloads/papers/stanley.cec02.pdf)
* [NEAT package Documentation](https://neat-python.readthedocs.io/en/latest/)

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

This program is not an original creation, I followed a serie of tutorials of the of the video maker Tech with Tim.
My goal objective was to improve my skills in Python.

Please watch the whole playlist with the explanations:
https://www.youtube.com/watch?v=MMxFDaIOHsE&list=PLzMcBGfZo4-lwGZWXz5Qgta_YNX3_vLS2
