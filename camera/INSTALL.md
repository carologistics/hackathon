# Kamera-Node aus dem Ordner `camera` installieren

Öffne für alle folgenden Befehle ein Terminal im Ordner `camera`. Dort liegen `include/`, `lib/` und `ros_ws/`.

## Voraussetzungen

- Linux x86-64 mit ROS 2 Humble unter `/opt/ros/humble`. Die mitgelieferte O3P-Bibliothek ist für x86-64 gebaut.
- CMake ab 3.24. Prüfe die Version mit `cmake --version`.
- Für den Funktionstest ist eine per USB angeschlossene O3P-Kamera erforderlich.

Installiere die zusätzlichen Pakete auf einem System mit eingerichteter ROS-2-Humble-Paketquelle.

```bash
sudo apt update
sudo apt install build-essential python3-colcon-common-extensions \
  libopencv-dev libusb-1.0-0 libudev1 \
  ros-humble-ament-cmake ros-humble-rclcpp ros-humble-ros2run \
  ros-humble-ros2topic ros-humble-sensor-msgs ros-humble-std-msgs \
  ros-humble-std-srvs ros-humble-diagnostic-msgs ros-humble-cv-bridge \
  ros-humble-tf2-ros ros-humble-geometry-msgs
```

## Bauen und installieren

```bash
source /opt/ros/humble/setup.bash
o3p_sdk_dir="$(pwd -P)"
colcon --log-base ros_ws/log-humble build \
  --base-paths ros_ws/src \
  --build-base ros_ws/build-humble --install-base ros_ws/install-humble \
  --packages-select o3p_node \
  --cmake-args -DO3P_DIR="$o3p_sdk_dir" \
  -DO3P_CREATE_CUSTOM_RVIZ_PANEL=OFF -DBUILD_TESTING=OFF
```

Colcon installiert den Node lokal unter `ros_ws/install-humble`. Die eigenen Build-Verzeichnisse umgehen alte CMake-Caches mit absoluten Pfaden. Die Installation verwendet die SDK-Bibliothek aus `camera/lib`. Wenn du den Ordner verschiebst, baue mit frischen Build- und Installationsverzeichnissen neu.

## Starten und prüfen

Lade im Ordner `camera` die ROS-Umgebung und starte den Node.

```bash
source /opt/ros/humble/setup.bash
source ros_ws/install-humble/setup.bash
ros2 run o3p_node camera_node --ros-args -p wait_for_device_timeout:=5.0
```

Bei erfolgreicher Verbindung meldet der Node die Seriennummer. Falls die Kamera beim Start nicht gefunden wird, prüfe mit `lsusb`, ob das System sie erkennt, und ob dein Linux-Benutzer Zugriff auf das USB-Gerät hat.

Öffne ein zweites Terminal in `camera` und prüfe, ob ein Tiefenbild ankommt.

```bash
source /opt/ros/humble/setup.bash
source ros_ws/install-humble/setup.bash
timeout 12s ros2 topic echo /camera/depth/image_raw \
  --field encoding --once --qos-reliability best_effort
```

Die erwartete Ausgabe ist `16UC1`. Beende den Node im ersten Terminal mit **Strg+C**.
