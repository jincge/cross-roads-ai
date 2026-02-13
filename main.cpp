#include <Windows.h>
#using <System.dll>
#using <System.Windows.Forms.dll>
#using <System.Drawing.dll>

#include "src/Intersection.h"
#include "src/ControlAlgorithm.h"
#include "src/SafetyChecker.h"
#include "src/TrafficGenerator.h"
#include "src/Simulation.h"

using namespace System;
using namespace System::Windows::Forms;
using namespace System::Drawing;
using namespace System::Threading;

public ref class MainForm : public Form {
public:
    MainForm() {
        this->Text = "Cross Road AI";
        this->Size = System::Drawing::Size(800, 600);

        runButton = gcnew Button();
        runButton->Text = "Start/Stop";
        runButton->AutoSize = true;
        runButton->Location = Point(20, 20);
        runButton->Click += gcnew EventHandler(this, &MainForm::OnRunClicked);
        this->Controls->Add(runButton);

        statusLabel = gcnew Label();
        statusLabel->Text = "Idle";
        statusLabel->AutoSize = true;
        statusLabel->Location = Point(20, 60);
        this->Controls->Add(statusLabel);

        drawPanel = gcnew Panel();
        drawPanel->Location = Point(150, 20);
        drawPanel->Size = Drawing::Size(600, 520);
        drawPanel->BorderStyle = BorderStyle::FixedSingle;
        drawPanel->Paint += gcnew PaintEventHandler(this, &MainForm::OnPaintPanel);
        this->Controls->Add(drawPanel);

        // Setup simulation (native objects)
        std::vector<std::string> approaches = {"north", "east", "south", "west"};
        Intersection intersection(approaches);

        std::vector<SignalPhase> phases;
        phases.emplace_back("north-south", 5, std::unordered_map<std::string, LightState>{{"north", LightState::Green}, {"south", LightState::Green}});
        phases.emplace_back("east-west", 5, std::unordered_map<std::string, LightState>{{"east", LightState::Green}, {"west", LightState::Green}});

        ControlAlgorithm algorithm("basic", phases);
        SafetyChecker safety;
        TrafficGenerator generator(intersection.approachIds());

        sim = new Simulation(std::move(intersection), std::move(algorithm), std::move(safety), std::move(generator));

        // Timer for stepping simulation
        ticker = gcnew System::Windows::Forms::Timer();
        ticker->Interval = 1000; // 1 second per step
        ticker->Tick += gcnew EventHandler(this, &MainForm::OnTick);
    }

    ~MainForm() {
        delete sim;
    }

private:
    Button ^ runButton;
    Label ^ statusLabel;
    Panel ^ drawPanel;
    System::Windows::Forms::Timer ^ ticker;

    Simulation *sim;
    bool running{false};

    void OnRunClicked(Object ^ sender, EventArgs ^ e) {
        if (!running) {
            sim->start();
            ticker->Start();
            running = true;
            statusLabel->Text = "Running";
        } else {
            ticker->Stop();
            sim->stop();
            running = false;
            statusLabel->Text = "Stopped";
        }
    }

    void OnTick(Object ^ sender, EventArgs ^ e) {
        sim->step();
        drawPanel->Invalidate();
    }

    void OnPaintPanel(Object ^ sender, PaintEventArgs ^ e) {
        Graphics ^g = e->Graphics;
        g->Clear(Color::White);

        // Draw intersection center
        int w = drawPanel->Width;
        int h = drawPanel->Height;
        int cx = w/2;
        int cy = h/2;
        int laneLength = 180;
        int laneWidth = 40;

        // Draw four approaches
        // North
        g->FillRectangle(Brushes::LightGray, cx - laneWidth/2, cy - laneLength - laneWidth/2, laneWidth, laneLength);
        // South
        g->FillRectangle(Brushes::LightGray, cx - laneWidth/2, cy + laneWidth/2, laneWidth, laneLength);
        // West
        g->FillRectangle(Brushes::LightGray, cx - laneLength - laneWidth/2, cy - laneWidth/2, laneLength, laneWidth);
        // East
        g->FillRectangle(Brushes::LightGray, cx + laneWidth/2, cy - laneWidth/2, laneLength, laneWidth);

        // Draw traffic lights
        auto &approaches = sim->intersection().approaches();
        for (size_t i=0; i<approaches.size(); ++i) {
            const RoadApproach &a = approaches[i];
            Point lightPos;
            switch (i) {
                case 0: lightPos = Point(cx - 10, cy - laneWidth/2 - 30); break; // north
                case 1: lightPos = Point(cx + laneWidth/2 + 30, cy - 10); break; // east
                case 2: lightPos = Point(cx - 10, cy + laneWidth/2 + 10); break; // south
                default: lightPos = Point(cx - laneWidth/2 - 30, cy - 10); break; // west
            }
            LightState state = a.light().getState();
            Brush ^brush = Brushes::Red;
            if (state == LightState::Green) brush = Brushes::Green;
            else if (state == LightState::FlashingAmber) brush = Brushes::Yellow;
            g->FillEllipse(brush, lightPos.X, lightPos.Y, 16, 16);
        }

        // Draw vehicles from recentSpawned
        const auto &spawned = sim->recentSpawned();
        int carSize = 12;
        for (const auto &sv : spawned) {
            int vx=0, vy=0;
            if (sv.approachId == "north") {
                vx = cx - carSize/2; vy = cy - laneLength - carSize - 4;
            } else if (sv.approachId == "south") {
                vx = cx - carSize/2; vy = cy + laneLength + 4;
            } else if (sv.approachId == "east") {
                vx = cx + laneLength + 4; vy = cy - carSize/2;
            } else { // west
                vx = cx - laneLength - carSize - 4; vy = cy - carSize/2;
            }
            g->FillRectangle(Brushes::Blue, vx, vy, carSize, carSize);
        }
    }
};

[STAThread]
int WINAPI WinMain(HINSTANCE, HINSTANCE, LPSTR, int) {
    Application::EnableVisualStyles();
    Application::SetCompatibleTextRenderingDefault(false);
    Application::Run(gcnew MainForm());
    return 0;
}