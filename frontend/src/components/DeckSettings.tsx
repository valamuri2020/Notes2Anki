import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Check } from 'lucide-react';

interface DeckSettingsProps {
    files: File[];
    multipleDecksSetting: boolean;
    setMultipleDecksSetting: (value: boolean) => void;
    outputFormat: 'apkg' | 'pdf' | 'csv';
    setOutputFormat: (format: 'apkg' | 'pdf' | 'csv') => void;
    deckNames: { [key: string]: string };
    setDeckNames: (names: { [key: string]: string }) => void;
}

export default function DeckSettings({
    files,
    multipleDecksSetting,
    setMultipleDecksSetting,
    outputFormat,
    setOutputFormat,
    deckNames,
    setDeckNames
}: DeckSettingsProps) {
    // Update deck names when files change
    useEffect(() => {
        const newDeckNames = { ...deckNames };
        files.forEach(file => {
            if (!newDeckNames[file.name]) {
                // Default deck name is the filename without extension
                newDeckNames[file.name] = file.name.split('.')[0];
            }
        });
        // Remove deck names for files that no longer exist
        Object.keys(newDeckNames).forEach(fileName => {
            if (!files.find(f => f.name === fileName)) {
                delete newDeckNames[fileName];
            }
        });
        setDeckNames(newDeckNames);
    }, [files]);

    return (
        <div className="glass-morphism rounded-xl p-6 mt-4">
            <h3 className="text-lg font-medium mb-4">Deck Settings</h3>
            
            {/* Multiple Decks Toggle */}
            <div className="mb-6">
                <label className="flex items-center space-x-3 cursor-pointer">
                    <div 
                        className={`w-10 h-6 rounded-full p-1 transition-colors duration-200 ease-in-out ${
                            multipleDecksSetting ? 'bg-[#3A7DFF]' : 'bg-gray-300'
                        }`}
                        onClick={() => setMultipleDecksSetting(!multipleDecksSetting)}
                    >
                        <div
                            className={`bg-white w-4 h-4 rounded-full shadow-md transform transition-transform duration-200 ease-in-out ${
                                multipleDecksSetting ? 'translate-x-4' : 'translate-x-0'
                            }`}
                        />
                    </div>
                    <span className="text-sm">Create Multiple Decks</span>
                </label>
                <p className="text-xs text-[#767676] mt-1 ml-13">
                    Create separate decks for each file
                </p>
            </div>

            {/* Output Format Selection */}
            <div className="mb-6">
                <label className="text-sm mb-2 block">Output Format</label>
                <div className="flex space-x-3">
                    {['apkg', 'pdf', 'csv'].map((format) => (
                        <button
                            key={format}
                            onClick={() => setOutputFormat(format as 'apkg' | 'pdf' | 'csv')}
                            className={`px-4 py-2 rounded-lg text-sm transition-colors duration-200 ${
                                outputFormat === format
                                    ? 'bg-[#3A7DFF] text-white'
                                    : 'bg-white/50 hover:bg-white/80'
                            }`}
                        >
                            .{format.toUpperCase()}
                        </button>
                    ))}
                </div>
            </div>

            {/* Deck Names (shown only when Multiple Decks is enabled) */}
            <AnimatePresence>
                {multipleDecksSetting && files.length > 0 && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="overflow-hidden"
                    >
                        <label className="text-sm mb-2 block">Deck Names</label>
                        <div className="space-y-3">
                            {files.map((file) => (
                                <div key={file.name} className="flex items-center space-x-3">
                                    <input
                                        type="text"
                                        value={deckNames[file.name] || ''}
                                        onChange={(e) => {
                                            const newDeckNames = { ...deckNames };
                                            newDeckNames[file.name] = e.target.value;
                                            setDeckNames(newDeckNames);
                                        }}
                                        placeholder="Enter deck name"
                                        className="flex-1 px-3 py-2 rounded-lg bg-white/50 focus:bg-white/80 
                                                 transition-colors duration-200 text-sm outline-none 
                                                 focus:ring-2 focus:ring-[#3A7DFF]/50"
                                    />
                                    <span className="text-xs text-[#767676] truncate max-w-[200px]">
                                        ({file.name})
                                    </span>
                                </div>
                            ))}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
} 