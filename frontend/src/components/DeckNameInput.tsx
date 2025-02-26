import { ChangeEvent } from "react";
import { motion } from "framer-motion";

interface DeckNameInputProps {
  deckName: string;
  setDeckName: (name: string) => void;
}

export default function DeckNameInput({ deckName, setDeckName }: DeckNameInputProps) {
  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    setDeckName(e.target.value);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="mt-6"
    >
      <label htmlFor="deckName" className="block text-sm font-medium text-[#767676] mb-2 ml-1">
        Deck Name
      </label>
      <input
        id="deckName"
        type="text"
        value={deckName}
        onChange={handleInputChange}
        placeholder="Enter deck name"
        className="glass-morphism px-4 py-3 rounded-lg border text-[#2C2C2C] outline-none focus:border-[#3A7DFF] focus:border transition-colors mx-auto border-gray-300"
      />
    </motion.div>
  );
} 