# O3P-Kameranode mit ROS 2 Humble

Führe die Befehle in einem normalen Desktop-Terminal aus. Beginne im
SDK-Hauptordner, in dem `examples/`, `include/`, `lib/` und `udev/` liegen.

## 1. Bauen

Vorausgesetzt werden ROS 2 Humble, `colcon`, CMake ab 3.24, die
OpenCV-4-Entwicklungsbibliotheken und die ROS-Abhängigkeiten aus
`src/o3p_node/package.xml`. In diesem Workspace war der folgende Build erfolgreich.
Das optionale RViz-Panel ist dabei deaktiviert.

```bash
source /opt/ros/humble/setup.bash
cd examples/ros_ws
colcon build --cmake-args -DO3P_DIR="$(realpath ../..)" -DO3P_CREATE_CUSTOM_RVIZ_PANEL=OFF
```

Wenn der vorhandene Build im selben SDK-Ordner liegt, kannst du direkt
mit Schritt 2 beginnen. Nach einem Umzug des SDK solltest du den Build
neu erzeugen, da der Node den absoluten Pfad zur SDK-Bibliothek verwendet.

## 2. Kamera anschließen und Node starten

Schließe die O3P-Kamera per USB an. Führe im Workspace `examples/ros_ws` aus:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch o3p_node camera_node.launch.py
```

Bei `Device not found` prüfe im Desktop-Terminal mit `lsusb`, ob Linux die
Kamera erkennt, und mit `ls -l /dev/o3p-*`, ob der Gerätelink vorhanden ist.
Wenn die Kamera per USB erkannt wird und der Link fehlt, folge der
[udev-Anleitung](../../udev/README.md) und stecke die Kamera anschließend neu an.

## 3. Datenempfang prüfen

Lass den Launch laufen und öffne ein zweites Terminal:

```bash
source /opt/ros/humble/setup.bash
ros2 node list
ros2 topic hz /camera/depth/image_raw
```

Mit den Standardeinstellungen erscheint `/o3p_camera` in der Node-Liste.
Wiederholte Ausgaben von `average rate` bestätigen den Empfang von Tiefenbildern.
Mit `Ctrl+C` beendest du die Messung oder den Launch im jeweiligen Terminal.

Der Build wurde in der Workspace-Sitzung geprüft. Diese Sitzung hatte keinen
Zugriff auf die USB-Gerätedateien und blockierte UDP-Sockets. Der Test mit
Live-Kameradaten erfolgt daher im Desktop-Terminal.

## Welche Ordner kann ich löschen?

Die Pfade in der Tabelle beziehen sich auf den SDK-Hauptordner.

| Ordner | Verwendung |
| --- | --- |
| `examples/ros_ws/log/` | Colcon-Buildprotokolle. Löschbar und beim nächsten Build neu erzeugt. |
| `examples/ros_ws/build/` | CMake-Cache und Zwischenprodukte. Beim obigen Build ohne `--symlink-install` bleibt der installierte Node nutzbar. Der nächste Build kompiliert erneut. |
| `examples/ros_ws/install/` | Enthält den startbaren Node und die Workspace-Umgebung. Für den Start behalten. Nach dem Löschen zuerst Schritt 1 ausführen. |
| `examples/build/` | Separater Build-Ordner der SDK-Beispiele. Für den ROS-Node entbehrlich. |
| `bin/`, `doc/`, `python/` | Für den ROS-Node entbehrlich. Behalten, wenn du die SDK-Programme, Dokumentation oder Python-Schnittstelle brauchst. |
| Andere Beispielordner unter `examples/` | Für den ROS-Node entbehrlich. `examples/ros_ws/` für ROS behalten. |
| `examples/ros_ws/src/`, `include/` | ROS-Quellcode und SDK-Header. Für spätere Builds behalten. |
| `lib/` | SDK-Bibliotheken einschließlich `libo3p.so`. Für den Build und den Betrieb behalten. |
| `udev/` | USB-Regel und Einrichtungsanleitung. Für eine spätere Einrichtung behalten. |

Für einen sauberen Neubau kannst du nach dem Beenden des Nodes
`examples/ros_ws/build/`, `examples/ros_ws/install/` und
`examples/ros_ws/log/` entfernen. Führe Schritt 1 danach in einem frischen
Terminal aus.
