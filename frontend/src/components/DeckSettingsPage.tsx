import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, Check, FileText } from 'lucide-react';

interface DeckSettingsPageProps {
    files: File[];
    onBack: () => void;
    onSubmit: () => void;
    multipleDecksSetting: boolean;
    setMultipleDecksSetting: (value: boolean) => void;
    outputFormat: 'apkg' | 'pdf' | 'csv';
    setOutputFormat: (format: 'apkg' | 'pdf' | 'csv') => void;
    deckNames: { [key: string]: string };
    setDeckNames: (names: { [key: string]: string }) => void;
}

export default function DeckSettingsPage({
    files,
    onBack,
    onSubmit,
    multipleDecksSetting,
    setMultipleDecksSetting,
    outputFormat,
    setOutputFormat,
    deckNames,
    setDeckNames
}: DeckSettingsPageProps) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="max-w-2xl mx-auto w-full"
        >
            {/* Header */}
            <h2 className="text-2xl font-medium mb-8 text-[#2C2C2C]">Deck Settings</h2>

            <div className="space-y-6">
                {/* Multiple Decks Toggle - More Compact */}
                {files.length > 1 && (
                    <div className="glass-morphism p-4 rounded-xl">
                        <div className="flex items-center justify-between">
                            <div>
                                <h3 className="text-base font-medium text-[#2C2C2C]">Multiple Decks</h3>
                                <p className="text-xs text-[#767676]">Create a separate deck for each file</p>
                            </div>
                            <button
                                onClick={() => setMultipleDecksSetting(!multipleDecksSetting)}
                                className={`relative w-11 h-6 rounded-full transition-colors duration-200 
                                    ${multipleDecksSetting ? 'bg-[#3A7DFF]' : 'bg-gray-200'}`}
                            >
                                <motion.div
                                    initial={false}
                                    animate={{
                                        x: multipleDecksSetting ? 20 : 2,
                                        scale: multipleDecksSetting ? 1 : 0.9
                                    }}
                                    className="absolute top-1 left-0 w-4 h-4 bg-white rounded-full shadow-sm"
                                />
                            </button>
                        </div>
                    </div>
                )}

                {/* Output Format Selection - Simplified */}
                <div className="glass-morphism p-4 rounded-xl">
                    <h3 className="text-base font-medium text-[#2C2C2C] mb-3">Output Format</h3>
                    <div className="grid grid-cols-3 gap-2">
                        {['apkg', 'pdf', 'csv'].map((format) => (
                            <button
                                key={format}
                                onClick={() => setOutputFormat(format as 'apkg' | 'pdf' | 'csv')}
                                className={`p-2 rounded-lg text-center transition-all duration-200 text-sm
                                    ${outputFormat === format
                                        ? 'bg-[#3A7DFF] text-white shadow-lg shadow-blue-500/20'
                                        : 'bg-white/50 hover:bg-white/80 text-[#2C2C2C]'
                                    }`}
                            >
                                .{format.toUpperCase()}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Deck Names */}
                <div className="glass-morphism p-4 rounded-xl">
                    <h3 className="text-base font-medium text-[#2C2C2C] mb-3">
                        {multipleDecksSetting ? 'Deck Names' : 'Deck Name'}
                    </h3>
                    
                    {/* Show all files when in single deck mode */}
                    {!multipleDecksSetting && (
                        <div className="mb-3 p-2 bg-gray-50 rounded-lg border border-gray-100">
                            <p className="text-xs font-medium text-[#767676] mb-2">Selected Files:</p>
                            <div className="space-y-1.5">
                                {files.map((file) => (
                                    <div key={file.name} className="flex items-center gap-2">
                                        <FileText className="w-3.5 h-3.5 text-[#767676]" />
                                        <span className="text-xs text-[#767676] truncate">
                                            {file.name}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    <div className="space-y-3">
                        {(multipleDecksSetting ? files : [files[0]]).map((file) => (
                            <div key={file.name} className="group">
                                {multipleDecksSetting && (
                                    <div className="flex items-center gap-2 mb-1.5">
                                        <FileText className="w-4 h-4 text-[#767676]" />
                                        <span className="text-xs text-[#767676] truncate">
                                            {file.name}
                                        </span>
                                    </div>
                                )}
                                <div className="relative">
                                    <input
                                        type="text"
                                        value={deckNames[file.name] || ''}
                                        onChange={(e) => {
                                            const newDeckNames = { ...deckNames };
                                            newDeckNames[file.name] = e.target.value;
                                            setDeckNames(newDeckNames);
                                        }}
                                        placeholder="Enter deck name"
                                        className="w-full px-3 py-2 rounded-lg bg-white 
                                                 transition-all duration-200 text-sm outline-none
                                                 border border-gray-200 hover:border-gray-300
                                                 focus:border-[#3A7DFF] focus:ring-2 focus:ring-[#3A7DFF]/20
                                                 placeholder-[#767676]"
                                    />
                                    <div className="absolute inset-0 -z-10 bg-gradient-to-b from-white/50 to-gray-50 rounded-lg" />
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Navigation Buttons */}
                <div className="flex items-center justify-between pt-4">
                    <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={onBack}
                        className="p-2 hover:bg-black/5 rounded-full transition-colors"
                    >
                        <ArrowLeft className="w-5 h-5 text-[#2C2C2C]" />
                    </motion.button>
                    <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={onSubmit}
                        className="bg-[#3A7DFF] hover:bg-[#316BDF] text-white px-8 py-3 rounded-lg 
                                 text-base font-medium transition-colors shadow-lg shadow-blue-500/20"
                    >
                        Generate ⚡️
                    </motion.button>
                </div>
            </div>
        </motion.div>
    );
} 