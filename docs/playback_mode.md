## Playback Mode
`QMediaPlaylist` supports 5 playback modes:

| Constant                            | Value | Description                                                  |
| ----------------------------------- | ----- | ------------------------------------------------------------ |
| `QMediaPlaylist::CurrentItemOnce`   | `0`   | The current item is played only once.                        |
| `QMediaPlaylist::CurrentItemInLoop` | `1`   | The current item is played repeatedly in a loop.             |
| `QMediaPlaylist::Sequential`        | `2`   | Playback starts from the current and moves through each successive item until the last is reached and then stops. The next item is a null item when the last one is currently playing. |
| `QMediaPlaylist::Loop`              | `3`   | Playback restarts at the first item after the last has finished playing. |
| `QMediaPlaylist::Random`            | `4`   | Play items in random order.                                  |

Except for the `CurrentItemOnce` playback mode, all other playback modes are used by Groove.

## Playback logic
There are two buttons in Groove's play bar to control the playback logic, namely random playback button and loop mode button.

The random playback button includes two states: `selected` and `not selected`. And The loop mode button includes three states: `Sequential`、`Loop` and `CurrentItemInLoop`. The corresponding relationship between the state combination of the two buttons and the playback state of `QMediaPlaylist` is shown in the following table:

| Button Status                       | Playback Mode       |
| ----------------------------------- | ------------------- |
| `not selected` + `Sequential`        | `Sequential`        |
| `not selected` + `Loop`              | `Loop`              |
| `not selected` + `CurrentItemInLoop` | `CurrentItemInLoop` |
| `selected` + `Sequential`            | `Random`            |
| `selected` + `Loop`                  | `Random`            |
| `selected` + `CurrentItemInLoop`     | `CurrentItemInLoop` |

When the playback mode is `CurrentItemInLoop`, no matter whether the random playback button is selected, clicking the next song button will select the next song in the order of the playing playlist instead of randomly selecting one.
