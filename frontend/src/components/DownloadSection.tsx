// src/components/DownloadSection.tsx
import { motion } from "framer-motion";
import { Check, Download, Share2 } from "lucide-react";

export default function DownloadSection() {
    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="glass-morphism rounded-xl p-12 text-center relative overflow-hidden"
        >
            {/* Success checkmark animation */}
            <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{
                    type: "spring",
                    stiffness: 200,
                    damping: 20
                }}
                className="mb-6"
            >
                <div className="w-16 h-16 bg-[#3A7DFF]/10 rounded-full flex items-center justify-center mx-auto">
                    <Check className="w-8 h-8 text-[#3A7DFF]" />
                </div>
            </motion.div>

            {/* Success message */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
            >
                <h2 className="text-2xl font-semibold mb-2">
                    Your flashcards are ready!
                </h2>
                <p className="text-[#767676] mb-8">
                    Download your Anki package below
                </p>

                {/* File info */}
                <div className="mb-6 p-3 bg-white/50 rounded-lg inline-block">
                    <p className="text-sm text-[#767676]">
                        Package: MyNotes.apkg (2.3 MB)
                    </p>
                </div>

                {/* Actions */}
                <div className="flex flex-col items-center gap-4">
                    <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        className="bg-[#3A7DFF] hover:bg-[#316BDF] text-white px-8 py-3 rounded-lg 
                     flex items-center gap-2 font-medium transition-colors shadow-lg 
                     shadow-blue-500/20"
                        onClick={() => {
                            // TODO: Implement actual download
                            alert("Download functionality will be implemented");
                        }}
                    >
                        <Download className="w-5 h-5" />
                        Download Now
                    </motion.button>

                    <button
                        className="text-[#2C2C2C] hover:text-[#316BDF] transition-colors 
                     flex items-center gap-2 text-sm"
                        onClick={() => {
                            // TODO: Implement sharing functionality
                            alert("Share functionality will be implemented");
                        }}
                    >
                        <Share2 className="w-4 h-4" />
                        Share with others
                    </button>
                </div>
            </motion.div>

            {/* Optional: Add subtle confetti animation here */}
        </motion.div>
    );
}