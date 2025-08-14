import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Loader2, Play, Video, Sparkles } from "lucide-react";
import { toast } from "sonner";

interface VideoGeneratorProps {
  onVideoGenerated?: (videoUrl: string) => void;
}

interface GenerationStatus {
  isGenerating: boolean;
  progress: number;
  message: string;
}

export const VideoGenerator = ({ onVideoGenerated }: VideoGeneratorProps) => {
  const [topic, setTopic] = useState("");
  const [status, setStatus] = useState<GenerationStatus>({
    isGenerating: false,
    progress: 0,
    message: ""
  });
  const [generatedVideoUrl, setGeneratedVideoUrl] = useState<string | null>(null);

  const simulateProgress = (onComplete: () => void) => {
    const stages = [
      { progress: 10, message: "Analyzing topic..." },
      { progress: 25, message: "Generating script..." },
      { progress: 45, message: "Creating visuals..." },
      { progress: 65, message: "Adding animations..." },
      { progress: 85, message: "Finalizing video..." },
      { progress: 100, message: "Video complete!" }
    ];

    let currentStage = 0;
    const updateProgress = () => {
      if (currentStage < stages.length) {
        setStatus(prev => ({
          ...prev,
          ...stages[currentStage]
        }));
        currentStage++;
        setTimeout(updateProgress, 2000);
      } else {
        onComplete();
      }
    };
    updateProgress();
  };

  const handleGenerateVideo = async () => {
  if (!topic.trim()) {
    toast.error("Please enter a topic for your video");
    return;
  }

  setStatus({ isGenerating: true, progress: 0, message: "Initializing..." });
  setGeneratedVideoUrl(null);

  try {
    const response = await fetch("http://localhost:8000/generate_video", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic }),
    });

    const data = await response.json();
    if (data.video_url) {
      // Wait a bit to simulate progress while the video generates
      simulateProgress(() => {
        setGeneratedVideoUrl(data.video_url);
        setStatus({
          isGenerating: false,
          progress: 100,
          message: "Video generated successfully!"
        });
        toast.success("Video generated successfully!");
      });
    }
  } catch (error) {
    console.error("Error generating video:", error);
    setStatus({ isGenerating: false, progress: 0, message: "" });
    toast.error("Failed to generate video. Please try again.");
  }
};


  return (
    <div className="w-full max-w-2xl mx-auto space-y-8">
      {/* Input Section */}
      <Card className="backdrop-blur-glass border-primary/20 p-8 animate-float">
        <div className="space-y-6">
          <div className="text-center space-y-2">
            <div className="flex items-center justify-center gap-2 text-primary">
              <Video className="w-6 h-6" />
              <Sparkles className="w-5 h-5 animate-pulse" />
            </div>
            <h2 className="text-2xl font-bold bg-gradient-primary bg-clip-text text-transparent">
              Create Your Video
            </h2>
            <p className="text-muted-foreground">
              Enter any topic and we'll generate an amazing video for you
            </p>
          </div>

          <div className="space-y-4">
            <div className="relative">
              <Input
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="Enter your topic..."
                className="bg-secondary/50 border-primary/20 focus:border-primary h-12 text-lg"
                disabled={status.isGenerating}
              />
            </div>

            <Button
              onClick={handleGenerateVideo}
              disabled={status.isGenerating || !topic.trim()}
              className="w-full h-12 bg-gradient-primary hover:opacity-90 transition-all duration-300 text-lg font-medium"
            >
              {status.isGenerating ? (
                <div className="flex items-center gap-2">
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Generating Video...
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <Play className="w-5 h-5" />
                  Generate Video
                </div>
              )}
            </Button>
          </div>
        </div>
      </Card>

      {/* Progress Section */}
      {status.isGenerating && (
        <Card className="backdrop-blur-glass border-accent/20 p-6 animate-pulse-glow">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-accent">
                {status.message}
              </span>
              <span className="text-sm text-muted-foreground">
                {status.progress}%
              </span>
            </div>
            
            <div className="w-full bg-secondary/50 rounded-full h-3">
              <div
                className="bg-gradient-accent h-3 rounded-full transition-all duration-500 ease-out"
                style={{ width: `${status.progress}%` }}
              />
            </div>
          </div>
        </Card>
      )}

      {/* Video Result Section */}
      {generatedVideoUrl && (
        <Card className="backdrop-blur-glass border-accent/20 p-6 animate-float">
          <div className="space-y-4">
            <div className="text-center">
              <h3 className="text-xl font-bold text-accent mb-2">
                Your Video is Ready!
              </h3>
              <p className="text-sm text-muted-foreground">
                Topic: {topic}
              </p>
            </div>
            
            <div className="relative rounded-lg overflow-hidden bg-black">
              <video
                controls
                className="w-full aspect-video"
                src={generatedVideoUrl}
                preload="metadata"
              >
                Your browser does not support the video tag.
              </video>
            </div>

            <div className="flex gap-2">
              <Button
                variant="outline"
                className="flex-1 border-accent/20 hover:bg-accent/10"
                onClick={() => {
                  const link = document.createElement('a');
                  link.href = generatedVideoUrl;
                  link.download = `${topic.replace(/\s+/g, '_')}_video.mp4`;
                  link.click();
                }}
              >
                Download Video
              </Button>
              <Button
                variant="outline"
                className="flex-1 border-primary/20 hover:bg-primary/10"
                onClick={() => {
                  setTopic("");
                  setGeneratedVideoUrl(null);
                  setStatus({ isGenerating: false, progress: 0, message: "" });
                }}
              >
                Generate Another
              </Button>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};