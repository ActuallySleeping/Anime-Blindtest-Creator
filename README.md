# Installation

To install the packages, run the following command in the terminal:

```bash
pip install -r requirements.txt
```

ImageMagick is also required to run the program. More information can be found [here](https://imagemagick.org/script/download.php).

# Usage

To run the program, run the following command in the terminal:

```bash
python3 main.py [Openings/Endings]
```

by default, the program will run to generate the blindtest for the first category within the config.json animes section.

# Configuration

To add an opening to be fetch and added to the blindtest, add the following to the config.json file:

```json
{
    "animes": [
        {
            "<CATEGORY>": [
                "...",
                "Video_Name.webm or Video_Name.mp4",
            ]
        }
    ]
}
```

You can find the name of the file for the video on the animethemes page on [animethemes.moe](https://animethemes.moe/).

Search your anime, and click on the opening you want to add.  
Right click on the video, and click on "Copy video link".  
You can then paste the address in the config.json file, and remove the "https://v.animethemes.moe/" part.  

For example, if the link is "https://v.animethemes.moe/OP1-SteinsGate.webm", you should write "OP1-SteinsGate.webm" in the config.json file.