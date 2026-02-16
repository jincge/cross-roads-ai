#include <QApplication>
#include <QLabel>
#include <QPainter>
#include <QRandomGenerator>
#include <QStringList>
#include <QTimer>
#include <QVBoxLayout>
#include <QWidget>
#include <algorithm>
#include <string>
#include <unordered_map>
#include <vector>

#include "src/ControlAlgorithm.h"
#include "src/Intersection.h"
#include "src/LightState.h"
#include "src/SafetyChecker.h"
#include "src/SignalPhase.h"
#include "src/Simulation.h"
#include "src/TrafficGenerator.h"

namespace {
QColor lightColor(LightState state) {
    switch (state) {
    case LightState::Green:
        return QColor(0, 180, 0);
    case LightState::Amber:
        return QColor(255, 170, 0);
    case LightState::FlashingAmber:
        return QColor(255, 200, 0);
    case LightState::AllRed:
    case LightState::Red:
    default:
        return QColor(200, 0, 0);
    }
}

QString lightName(LightState state) {
    switch (state) {
    case LightState::Green:
        return "Green";
    case LightState::Amber:
        return "Amber";
    case LightState::FlashingAmber:
        return "FlashingAmber";
    case LightState::AllRed:
        return "AllRed";
    case LightState::Red:
    default:
        return "Red";
    }
}

bool isGreen(LightState state) { return state == LightState::Green; }

struct RenderVehicle {
    QString approach;
    double position;
    bool stopped{false};
    QString type;
};
} // namespace

class MapView : public QWidget {
public:
    explicit MapView(QWidget *parent = nullptr) : QWidget(parent) { setMinimumSize(520, 520); }

    void setLights(const QMap<QString, LightState> &states) { lightStates = states; }

    void addSpawnedVehicles(const std::vector<SpawnedVehicle> &spawned, double spawnProbability) {
        for (const auto &spawn : spawned) {
            if (QRandomGenerator::global()->bounded(1.0) > spawnProbability) {
                continue;
            }
            RenderVehicle vehicle;
            vehicle.approach = QString::fromStdString(spawn.approachId);
            vehicle.position = 0.0;
            vehicle.type = QString::fromStdString(spawn.vehicle.type);
            vehicles.push_back(vehicle);
        }
    }

    void advance(double dtSeconds) {
        const double stopPos = laneLength - stopLineDistance;
        const double totalPath = laneLength * 2.0;
        const double move = speed * dtSeconds;

        for (auto &vehicle : vehicles) {
            const LightState state = lightStates.value(vehicle.approach, LightState::AllRed);
            if (!isGreen(state) && vehicle.position < stopPos) {
                if (vehicle.position + move >= stopPos) {
                    vehicle.position = stopPos;
                    vehicle.stopped = true;
                } else {
                    vehicle.position += move;
                    vehicle.stopped = false;
                }
            } else {
                vehicle.position += move;
                vehicle.stopped = false;
            }
        }

        vehicles.erase(std::remove_if(vehicles.begin(), vehicles.end(),
                                      [totalPath](const RenderVehicle &vehicle) {
                                          return vehicle.position > totalPath;
                                      }),
                       vehicles.end());
    }

protected:
    void paintEvent(QPaintEvent *event) override {
        Q_UNUSED(event);
        QPainter painter(this);
        painter.setRenderHint(QPainter::Antialiasing, true);

        painter.fillRect(rect(), QColor(25, 25, 25));

        const QPointF center = rect().center();
        const double roadWidth = 70.0;
        const double laneOffset = 16.0;

        painter.setPen(Qt::NoPen);
        painter.setBrush(QColor(60, 60, 60));
        painter.drawRect(QRectF(center.x() - roadWidth / 2.0, rect().top(), roadWidth, rect().height()));
        painter.drawRect(QRectF(rect().left(), center.y() - roadWidth / 2.0, rect().width(), roadWidth));

        QPen stopPen(QColor(240, 240, 240));
        stopPen.setWidth(3);
        painter.setPen(stopPen);
        painter.drawLine(QPointF(center.x() - roadWidth / 2.0, center.y() - stopLineDistance),
                         QPointF(center.x() + roadWidth / 2.0, center.y() - stopLineDistance));
        painter.drawLine(QPointF(center.x() - roadWidth / 2.0, center.y() + stopLineDistance),
                         QPointF(center.x() + roadWidth / 2.0, center.y() + stopLineDistance));
        painter.drawLine(QPointF(center.x() - stopLineDistance, center.y() - roadWidth / 2.0),
                         QPointF(center.x() - stopLineDistance, center.y() + roadWidth / 2.0));
        painter.drawLine(QPointF(center.x() + stopLineDistance, center.y() - roadWidth / 2.0),
                         QPointF(center.x() + stopLineDistance, center.y() + roadWidth / 2.0));

        drawLight(painter, "north", QPointF(center.x() - laneOffset, center.y() - stopLineDistance - 18.0));
        drawLight(painter, "south", QPointF(center.x() + laneOffset, center.y() + stopLineDistance + 18.0));
        drawLight(painter, "west", QPointF(center.x() - stopLineDistance - 18.0, center.y() + laneOffset));
        drawLight(painter, "east", QPointF(center.x() + stopLineDistance + 18.0, center.y() - laneOffset));

        for (const auto &vehicle : vehicles) {
            QColor color = (vehicle.type == "truck") ? QColor(140, 140, 220) : QColor(80, 170, 255);
            painter.setBrush(color);
            QPen vehiclePen(vehicle.stopped ? QColor(255, 80, 80) : QColor(30, 30, 30));
            vehiclePen.setWidth(2);
            painter.setPen(vehiclePen);

            const QPointF pos = vehiclePosition(center, laneOffset, vehicle);
            painter.drawEllipse(pos, 6.0, 6.0);
        }
    }

private:
    QPointF vehiclePosition(const QPointF &center, double laneOffset, const RenderVehicle &vehicle) const {
        if (vehicle.approach == "north") {
            return QPointF(center.x() - laneOffset, center.y() - laneLength + vehicle.position);
        }
        if (vehicle.approach == "south") {
            return QPointF(center.x() + laneOffset, center.y() + laneLength - vehicle.position);
        }
        if (vehicle.approach == "east") {
            return QPointF(center.x() + laneLength - vehicle.position, center.y() - laneOffset);
        }
        return QPointF(center.x() - laneLength + vehicle.position, center.y() + laneOffset);
    }

    void drawLight(QPainter &painter, const QString &approach, const QPointF &pos) const {
        const LightState state = lightStates.value(approach, LightState::AllRed);
        painter.setBrush(lightColor(state));
        painter.setPen(Qt::NoPen);
        painter.drawEllipse(pos, 6.5, 6.5);
    }

    QMap<QString, LightState> lightStates;
    std::vector<RenderVehicle> vehicles;
    double laneLength{200.0};
    double stopLineDistance{45.0};
    double speed{75.0};
};

class SimulationWindow : public QWidget {
public:
    SimulationWindow() : simulation(buildSimulation()) {
        auto *layout = new QVBoxLayout(this);
        layout->setContentsMargins(12, 12, 12, 12);
        layout->setSpacing(8);

        phaseLabel = new QLabel("Phase: --", this);
        phaseLabel->setStyleSheet("color: white; font-weight: bold;");
        spawnLabel = new QLabel("Spawns: --", this);
        spawnLabel->setStyleSheet("color: white;");
        countsLabel = new QLabel("Counts: --", this);
        countsLabel->setStyleSheet("color: white;");

        layout->addWidget(phaseLabel);
        layout->addWidget(spawnLabel);
        layout->addWidget(countsLabel);

        mapView = new MapView(this);
        layout->addWidget(mapView, 1);

        setWindowTitle("Cross-Roads AI Simulation");
        setStyleSheet("background-color: #1c1c1c;");

        updateLights();
        updateLabels({});

        connect(&stepTimer, &QTimer::timeout, this, [this]() {
            simulation.step();
            updateLights();

            const auto &spawned = simulation.recentSpawned();
            const double spawnProbability = QRandomGenerator::global()->bounded(0.3, 0.9);
            mapView->addSpawnedVehicles(spawned, spawnProbability);
            updateLabels(spawned);
        });
        stepTimer.start(1000);

        connect(&animationTimer, &QTimer::timeout, this, [this]() {
            mapView->advance(0.05);
            mapView->update();
        });
        animationTimer.start(50);
    }

private:
    static Simulation buildSimulation() {
        std::vector<std::string> directions{"north", "south", "east", "west"};
        Intersection intersection(directions);

        std::vector<SignalPhase> phases;
        phases.emplace_back("north-green", 5,
                            std::unordered_map<std::string, LightState>{{"north", LightState::Green}});
        phases.emplace_back("east-green", 5,
                            std::unordered_map<std::string, LightState>{{"east", LightState::Green}});
        phases.emplace_back("south-green", 5,
                            std::unordered_map<std::string, LightState>{{"south", LightState::Green}});
        phases.emplace_back("west-green", 5,
                            std::unordered_map<std::string, LightState>{{"west", LightState::Green}});

        ControlAlgorithm algorithm("clock-driven", phases);
        algorithm.setMode("fixed-schedule");

        SafetyChecker safety;
        TrafficGenerator generator(directions);
        generator.setArrivalPattern("randomized");

        Simulation simulation(std::move(intersection), std::move(algorithm), std::move(safety), std::move(generator));
        simulation.start();
        return simulation;
    }

    void updateLights() {
        QMap<QString, LightState> states;
        for (const auto &approach : simulation.intersection().approaches()) {
            states[QString::fromStdString(approach.direction())] = approach.light().getState();
        }
        mapView->setLights(states);
    }

    void updateLabels(const std::vector<SpawnedVehicle> &spawned) {
        const auto &approaches = simulation.intersection().approaches();

        QStringList countParts;
        for (const auto &approach : approaches) {
            const QString direction = QString::fromStdString(approach.direction());
            const QString light = lightName(approach.light().getState());
            countParts << QString("%1=%2 (%3)")
                              .arg(direction)
                              .arg(approach.sensor().getCount())
                              .arg(light);
        }

        phaseLabel->setText("Phase: " + QString::fromStdString(simulation.controlAlgorithm().getName()));
        spawnLabel->setText(QString("Spawns: %1 in last tick").arg(spawned.size()));
        countsLabel->setText("Counts: " + countParts.join(" | "));
    }

    Simulation simulation;
    MapView *mapView{nullptr};
    QLabel *phaseLabel{nullptr};
    QLabel *spawnLabel{nullptr};
    QLabel *countsLabel{nullptr};
    QTimer stepTimer;
    QTimer animationTimer;
};

int main(int argc, char **argv) {
    QApplication app(argc, argv);

    SimulationWindow window;
    window.resize(700, 760);
    window.show();

    return app.exec();
}
