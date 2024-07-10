# Usage
## Basic introduction
```shell
python rpgmvtransl.py -d $original_data -s $rpgmaker_script -t $translated_data [-e]
```
- Parameters
  - `-d`, `--data`: Path to the game's `data` folder.
  - `-s`, `--rpgmaker-script`: Path to the script that was initially extracted.
  - `-t`, `--translated-data`: Output path to the game data file.

## Usage steps
1. Extract game data.
2. Export data to [TkTransl][TkTranslRepo] for translation.
3. Inject translation into game data.
4. Copy data to game directory, overwriting original files. (It is best to create a backup first)

```shell
# Extract game data
python rpgmvtransl.py extract -d /Game/RPGMakerMX/example/www/data -s /working/sdata

# Copy data to TkTransl for translation
cp /working/sdata /tktransl/projects/example/input
python /tktransl/tktransl.py example galtransl-v1

# Inject GalTransl translation into game data
python rpgmvtransl.py -d /Game/RPGMakerMX/example/www/data -s /tktransl/projects/example/output -t /working/tdata

# Copy the translated data file to the game directory (remember to create a backup first)
cp -r /Game/RPGMakerMX/example/www/data /Game/RPGMakerMX/example/www/data.bak
cp -rf /working/tdata /Game/RPGMakerMX/example/www/data
```

[TkTranslRepo]: https://github.com/thiliapr/TkTransl