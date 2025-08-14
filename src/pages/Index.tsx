import { VideoGenerator } from "@/components/VideoGenerator";
import { BackgroundEffects } from "@/components/BackgroundEffects";
import { Video, Sparkles, Zap } from "lucide-react";

const Index = () => {
  return (
    <div className="min-h-screen relative overflow-hidden">
      <BackgroundEffects />
      
      <div className="relative z-10 container mx-auto px-4 py-12">
        {/* Header */}
        <div className="text-center mb-16 space-y-6">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="p-3 rounded-full bg-gradient-primary animate-pulse-glow">
              <Video className="w-8 h-8 text-white" />
            </div>
            <div className="flex items-center gap-1">
              <Sparkles className="w-6 h-6 text-accent animate-pulse" />
              <Zap className="w-5 h-5 text-primary animate-pulse" style={{ animationDelay: "0.5s" }} />
            </div>
          </div>
          
          <h1 className="text-6xl md:text-7xl font-bold bg-gradient-primary bg-clip-text text-transparent mb-6 animate-float">
            Topic to Video
          </h1>
          
          <p className="text-xl md:text-2xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
            Transform any topic into a stunning video with the power of AI. 
            <br />
            <span className="text-accent font-medium">Just type, click, and watch the magic happen.</span>
          </p>
        </div>

        {/* Main Video Generator */}
        <VideoGenerator />

        {/* Footer */}
        <div className="text-center mt-16 text-muted-foreground">
          <p className="text-sm">
            Powered by advanced AI technology • Create unlimited videos
          </p>
        </div>
      </div>
    </div>
  );
};

export default Index;
