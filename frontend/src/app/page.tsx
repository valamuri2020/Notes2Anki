"use client";

import { useState, useEffect } from "react";
import { Toaster } from "react-hot-toast";
import { motion, AnimatePresence } from "framer-motion";
import FileUpload from "@/components/FileUpload";
import Header from "@/components/Header";
import CreativeLoader from "@/components/ProcessingLoader";
import DownloadSection from "@/components/DownloadSection";
import DeckSettingsPage from "@/components/DeckSettingsPage";
import KofiButton from "@/components/KofiButton";
import EmailCaptureModal from "@/components/EmailCaptureModal";
import { API_URL } from "@/lib/constants";
import { toast } from "react-hot-toast";

interface DownloadData {
  filename: string;
  blob: Blob;
  requestId: string;
  isZip?: boolean;
  files?: { name: string; size: number }[];
}

export default function Home() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [isDownloadReady, setIsDownloadReady] = useState(false);
  const [files, setFiles] = useState<File[]>([]);
  const [downloadData, setDownloadData] = useState<DownloadData | null>(null);
  const [multipleDecksSetting, setMultipleDecksSetting] = useState(false);
  const [outputFormat, setOutputFormat] = useState<'apkg' | 'pdf' | 'csv'>('apkg');
  const [deckNames, setDeckNames] = useState<{ [key: string]: string }>({});
  const [showSettings, setShowSettings] = useState(false);
  const [showEmailModal, setShowEmailModal] = useState(false);

  // Set default deck names from uploaded files (without extension)
  useEffect(() => {
    if (files.length > 0) {
      setDeckNames(prevDeckNames => {
        const newDeckNames = { ...prevDeckNames };
        let shouldUpdate = false;
        
        files.forEach(file => {
          if (!newDeckNames[file.name]) {
            newDeckNames[file.name] = file.name.replace(/\.[^/.]+$/, "");
            shouldUpdate = true;
          }
        });
        
        return shouldUpdate ? newDeckNames : prevDeckNames;
      });
    }
  }, [files]);

  const handleSubmit = async () => {
    if (files.length === 0) {
      toast.error("Please upload at least one file");
      return;
    }

    // Validate deck names
    if (multipleDecksSetting) {
      const emptyNames = Object.values(deckNames).some(name => !name.trim());
      if (emptyNames) {
        toast.error("Please enter names for all decks");
        return;
      }
    } else if (!deckNames[files[0].name]?.trim()) {
      toast.error("Please enter a deck name");
      return;
    }

    setIsProcessing(true);

    try {
      const formData = new FormData();
      files.forEach((file) => formData.append("files", file));

      const requestData = {
        id: crypto.randomUUID(),
        multiple_decks: multipleDecksSetting,
        output_format: outputFormat,
        deck_names: deckNames
      };

      formData.append("request", JSON.stringify(requestData));

      const response = await fetch(`${API_URL}/generate`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const blob = await response.blob();
      const requestId = response.headers.get("X-Request-ID");
      const contentDisposition = response.headers.get("Content-Disposition");
      const filename = contentDisposition?.split("filename=")[1]?.replace(/"/g, "") ||
        (multipleDecksSetting ? "decks.zip" : `${deckNames[files[0].name]}.${outputFormat}`);

      let filesList = undefined;
      if (multipleDecksSetting) {
        filesList = files.map(file => ({
          name: `${deckNames[file.name]}.${outputFormat}`,
          size: 0 // Size will be approximate or unknown until actually downloaded
        }));
      }

      setDownloadData({
        filename,
        blob,
        requestId: requestId || "",
        isZip: multipleDecksSetting,
        files: filesList
      });

      setIsProcessing(false);
      setIsDownloadReady(true);
    } catch (error) {
      console.error("Error generating deck:", error);
      setIsProcessing(false);
      setIsDownloadReady(false);
      toast.error("Oops, there was an error: " + error);
    }
  };

  const handleNext = () => {
    if (files.length === 0) {
      toast.error("Please upload at least one file");
      return;
    }
    setShowSettings(true);
  };

  const handleBack = () => {
    setShowSettings(false);
  };

  const handleEmailSubmit = async (email: string) => {
    try {
      // Send email to your backend
      await fetch(`${API_URL}/add_email`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email }),
      });
    } catch (error) {
      console.error("Error saving email:", error);
    }
    setShowEmailModal(false);
    handleDownload();
  };

  const handleDownloadClick = () => {
    setShowEmailModal(true);
  };

  const handleDownload = () => {
    if (!downloadData) return;
    
    const url = window.URL.createObjectURL(downloadData.blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = downloadData.filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  return (
    <main className="min-h-screen px-4 sm:px-6 py-8 sm:py-16 flex flex-col">
      <Toaster />
      <Header />
      <div className="max-w-4xl mx-auto mt-8 sm:mt-16 flex-grow w-full">
        <AnimatePresence mode="wait">
          {!isProcessing && !isDownloadReady && !showSettings && (
            <motion.div
              key="upload"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <FileUpload
                files={files}
                setFiles={setFiles}
              />

              <div className="mt-6 sm:mt-8 flex justify-center">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className={`w-1/2 sm:w-auto px-6 sm:px-8 py-3 rounded-lg text-white text-base sm:text-lg font-medium 
                    transition-colors shadow-lg shadow-blue-500/20
                    ${files.length === 0
                      ? 'bg-neutral-400 cursor-not-allowed'
                      : 'bg-[#3A7DFF] hover:bg-[#316BDF]'
                    }`}
                  onClick={handleNext}
                  disabled={files.length === 0}
                >
                  Next
                </motion.button>
              </div>
            </motion.div>
          )}

          {!isProcessing && !isDownloadReady && showSettings && (
            <DeckSettingsPage
              files={files}
              onBack={handleBack}
              onSubmit={handleSubmit}
              multipleDecksSetting={multipleDecksSetting}
              setMultipleDecksSetting={setMultipleDecksSetting}
              outputFormat={outputFormat}
              setOutputFormat={setOutputFormat}
              deckNames={deckNames}
              setDeckNames={setDeckNames}
            />
          )}

          {isProcessing && (
            <motion.div
              key="processing"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="glass-morphism rounded-xl p-6 sm:p-12 flex justify-center"
            >
              <CreativeLoader />
            </motion.div>
          )}

          {isDownloadReady && downloadData && (
            <>
              <div className="flex justify-end mb-4">
                <button
                  onClick={() => window.location.reload()}
                  className="text-sm text-[#767676] hover:text-[#2C2C2C] font-medium transition-colors flex items-center"
                >
                  Create Another &rarr;
                </button>
              </div>
              <DownloadSection 
                downloadData={downloadData} 
                onDownloadClick={handleDownloadClick}
              />
              <p className="text-xs text-[#767676] mt-6 text-center">AI can make mistakes. Please verify important information.</p>
            </>
          )}
        </AnimatePresence>
      </div>

      <KofiButton />

      <footer className="w-full mt-auto pt-8 pb-4 text-center text-xs sm:text-sm text-gray-500">
        <p>No data is permanently stored. Made with ❤️ by <a href="https://www.linkedin.com/in/valamuri/" target="_blank" rel="noopener noreferrer" className="hover:text-black underline transition-colors">Vivek Alamuri</a>.</p>
      </footer>

      <EmailCaptureModal
        isOpen={showEmailModal}
        onClose={() => setShowEmailModal(false)}
        onEmailSubmit={handleEmailSubmit}
      />
    </main>
  );
}