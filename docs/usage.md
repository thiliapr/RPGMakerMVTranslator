# Usage
## Basic introduction
```shell
python rpgmvtransl.py -d $original_data -s $rpgmaker_script -g $galtransl_script -t $translated_data [-e]
```
- Parameters
- `-d`, `--data`: Path to the game's `data` folder.
- `-s`, `--rpgmaker-script`: Path to the initial extracted script.
- `-g`, `--galtransl-script`: Input or output of [GalTransl][GalTranslRepo]. Usually `gt_input` or `gt_input`.
- `-t`, `--translated-data`: Output path to the game data file.

## Usage steps
```shell
# Extract game data
python rpgmvtransl.py extract -d /Game/RPGMakerMX/example/www/data -s /working/sdata

# Export data to GalTransl for translation
python rpgmvtransl.py galtransl -s /working/sdata -g /working/rpgmx-galtransl/gt_input
python galtransl/run_GalTransl.py /working/rpgmx-galtransl/config.yaml galtransl-v1

# Inject GalTransl translation into game data
python rpgmvtransl.py -d /Game/RPGMakerMX/example/www/data -s /working/sdata -g /working/rpgmx-galtransl/gt_output -t /working/tdata

# Copy the translated data file to the game directory (remember to create a backup first)
cp -r /Game/RPGMakerMX/example/www/data /Game/RPGMakerMX/example/www/data.bak
cp -rf /working/tdata /Game/RPGMakerMX/example/www/data
```

[GalTranslRepo]: https://github.com/XD2333/GalTransl