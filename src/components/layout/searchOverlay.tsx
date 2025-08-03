import { useState, useRef, useEffect } from "react";
import { FiSearch, FiChevronRight } from "react-icons/fi";

interface SearchOverlayProps {
  isOpen: boolean;
  onClose: () => void;
  initialQuery?: string;
}

const SearchOverlay = ({ isOpen, onClose, initialQuery = "" }: SearchOverlayProps) => {
  const [searchQuery, setSearchQuery] = useState(initialQuery);
  const modalInputRef = useRef<HTMLInputElement>(null);

  // Fokus auf das Suchfeld setzen, wenn das Modal geöffnet wird
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => {
        modalInputRef.current?.focus();
      }, 50);
    }
  }, [isOpen]);

  // Event-Listener für ESC-Taste
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape" && isOpen) {
        event.preventDefault();
        onClose();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, onClose]);

  // Wenn das Modal nicht geöffnet ist, nichts rendern
  if (!isOpen) return null;

  // Funktion zum Hervorheben des Suchbegriffs
  const highlightQuery = (text: string, query: string) => {
    if (!query.trim()) return text;

    const regex = new RegExp(`(${query})`, "gi");
    const parts = text.split(regex);

    return parts.map((part, i) => {
      if (part.toLowerCase() === query.toLowerCase()) {
        return (
          <span key={i} className="text-orange-500 font-medium">
            {part}
          </span>
        );
      }
      return part;
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-16 px-4 sm:px-6 md:px-8">
      {/* Hintergrund mit Blur-Effekt */}
      <div
        className="fixed inset-0 transition-opacity duration-300 ease-out backdrop-blur-sm bg-black/30"
        onClick={onClose}
        style={{ animation: "fadeIn 0.2s ease-out forwards" }}
      ></div>

      {/* Suchmodalfenster */}
      <div
        className="relative bg-white w-full max-w-xl rounded-lg shadow-xl overflow-hidden"
        style={{ animation: "slideDown 0.3s ease-out forwards, fadeIn 0.3s ease-out forwards" }}
      >
        {/* Suchleiste */}
        <div className="relative border-b">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <FiSearch className="h-5 w-5 text-gray-400" />
          </div>
          <input
            ref={modalInputRef}
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="block w-full pl-10 pr-12 py-3 border-0 text-base focus:ring-0 focus:outline-none"
            placeholder="Search documentation..."
            autoComplete="off"
          />
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
            <span className="text-xs px-2 py-0.5 bg-gray-100 rounded text-gray-500">ESC</span>
          </div>
        </div>

        {/* Suchergebnisse mit Scroll */}
        <div className="overflow-y-auto max-h-[60vh]">
          {/* AI-Antwort */}
          <div
            className="px-4 py-3 hover:bg-gray-50 cursor-pointer border-b border-gray-100"
            style={{ animation: "fadeInUp 0.3s ease-out 0.1s both" }}
          >
            <div className="flex items-start">
              <div className="flex-shrink-0 mr-3">
                <div className="w-8 h-8 bg-orange-500 rounded-md flex items-center justify-center text-white">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                    <path d="M11.25 5.337c0-.355-.186-.676-.401-.959a1.647 1.647 0 01-.349-1.003c0-1.036 1.007-1.875 2.25-1.875S15 2.34 15 3.375c0 .369-.128.713-.349 1.003-.215.283-.401.604-.401.959 0 .332.278.598.61.578 1.91-.114 3.79-.342 5.632-.676a.75.75 0 01.878.645 49.17 49.17 0 01.376 5.452.657.657 0 01-.66.664c-.354 0-.675-.186-.958-.401a1.647 1.647 0 00-1.003-.349c-1.035 0-1.875 1.007-1.875 2.25s.84 2.25 1.875 2.25c.369 0 .713-.128 1.003-.349.283-.215.604-.401.959-.401.31 0 .557.262.534.571a48.774 48.774 0 01-.595 4.845.75.75 0 01-.61.61c-1.82.317-3.673.533-5.555.642a.58.58 0 01-.611-.581c0-.355.186-.676.401-.959.221-.29.349-.634.349-1.003 0-1.035-1.007-1.875-2.25-1.875s-2.25.84-2.25 1.875c0 .369.128.713.349 1.003.215.283.401.604.401.959a.641.641 0 01-.658.643 49.118 49.118 0 01-4.708-.36.75.75 0 01-.645-.878c.293-1.614.504-3.257.629-4.924A.53.53 0 005.337 15c-.355 0-.676.186-.959.401-.29.221-.634.349-1.003.349-1.036 0-1.875-1.007-1.875-2.25s.84-2.25 1.875-2.25c.369 0 .713.128 1.003.349.283.215.604.401.959.401a.656.656 0 00.659-.663 47.703 47.703 0 00-.31-4.82.75.75 0 01.83-.832c1.343.155 2.703.254 4.077.294a.64.64 0 00.657-.642z" />
                  </svg>
                </div>
              </div>
              <div>
                <div className="flex items-center">
                  <div className="text-sm">
                    Can you tell me about <span className="text-orange-500 font-medium">browser</span>
                  </div>
                </div>
                <div className="text-xs text-gray-500 mt-0.5">Use AI to answer your question</div>
              </div>
              <div className="ml-auto flex items-center">
                <FiChevronRight className="text-orange-500" />
              </div>
            </div>
          </div>

          {/* Browser Settings */}
          <div
            className="px-4 py-2.5 hover:bg-gray-50 cursor-pointer border-b border-gray-100"
            style={{ animation: "fadeInUp 0.3s ease-out 0.15s both" }}
          >
            <div className="text-sm font-medium">{highlightQuery("Browser", searchQuery)} Settings</div>
            <div className="text-xs text-gray-500 mt-0.5">Browser Use allows you to customize the</div>
          </div>

          {/* Delete Browser Profile */}
          <div
            className="px-4 py-2.5 hover:bg-gray-50 cursor-pointer border-b border-gray-100"
            style={{ animation: "fadeInUp 0.3s ease-out 0.2s both" }}
          >
            <div className="flex items-center">
              <span className="inline-block px-1.5 py-0.5 bg-blue-100 text-blue-800 text-xs font-medium mr-2 rounded">
                POST
              </span>
              <span className="text-sm">
                Delete <span className="text-orange-500 font-medium">Browser</span> Profile For User
              </span>
            </div>
            <div className="text-xs text-gray-500 mt-0.5">Deletes the browser profile for the user.</div>
          </div>

          {/* Connect to your Browser */}
          <div
            className="px-4 py-2.5 hover:bg-gray-50 cursor-pointer border-b border-gray-100 flex items-center justify-between"
            style={{ animation: "fadeInUp 0.3s ease-out 0.25s both" }}
          >
            <div>
              <div className="text-sm">
                Connect to your <span className="text-orange-500 font-medium">Browser</span>
              </div>
              <div className="text-xs text-gray-500 mt-0.5">
                With this you can connect to your real browser, where you are logged
              </div>
            </div>
            <FiChevronRight className="text-orange-500" />
          </div>

          {/* Implementing the API */}
          <div
            className="px-4 py-2.5 hover:bg-gray-50 cursor-pointer border-b border-gray-100"
            style={{ animation: "fadeInUp 0.3s ease-out 0.3s both" }}
          >
            <div className="text-sm">Implementing the API</div>
            <div className="text-xs text-gray-500 mt-0.5">
              the API Learn how to implement the <span className="text-orange-500 font-medium">Browser</span> Use API in
              Python
            </div>
          </div>

          {/* Agent Settings */}
          <div
            className="px-4 py-2.5 hover:bg-gray-50 cursor-pointer border-b border-gray-100"
            style={{ animation: "fadeInUp 0.3s ease-out 0.35s both" }}
          >
            <div className="text-sm">
              Agent Settings › Reuse Existing <span className="text-orange-500 font-medium">Browser</span>
            </div>
            <div className="text-xs text-gray-500 mt-0.5">browser : A</div>
          </div>

          {/* Custom Functions */}
          <div
            className="px-4 py-2.5 hover:bg-gray-50 cursor-pointer border-b border-gray-100"
            style={{ animation: "fadeInUp 0.3s ease-out 0.4s both" }}
          >
            <div className="text-sm">
              Custom Functions › <span className="text-orange-500 font-medium">Browser</span>-Aware Functions
            </div>
            <div className="text-xs text-gray-500 mt-0.5">For actions that need browser access, simply add the</div>
          </div>

          {/* Development */}
          <div
            className="px-4 py-2.5 hover:bg-gray-50 cursor-pointer border-b border-gray-100"
            style={{ animation: "fadeInUp 0.3s ease-out 0.45s both" }}
          >
            <div className="text-sm">Development › Telemetry › Overview</div>
            <div className="text-xs text-gray-500 mt-0.5">
              <span className="text-orange-500 font-medium">Browser</span> Use collects anonymous usage data to help us
            </div>
          </div>

          {/* Get Started */}
          <div
            className="px-4 py-2.5 hover:bg-gray-50 cursor-pointer border-b border-gray-100"
            style={{ animation: "fadeInUp 0.3s ease-out 0.5s both" }}
          >
            <div className="text-sm">Get Started › Introduction › Overview</div>
            <div className="text-xs text-gray-500 mt-0.5">
              <span className="text-orange-500 font-medium">Browser</span> Use is the easiest way to connect your AI
              agents with the browser. It m
            </div>
          </div>

          {/* Lifecycle Hooks */}
          <div
            className="px-4 py-2.5 hover:bg-gray-50 cursor-pointer border-b border-gray-100"
            style={{ animation: "fadeInUp 0.3s ease-out 0.55s both" }}
          >
            <div className="text-sm">Lifecycle Hooks › Client Component (client.py)</div>
            <div className="text-xs text-gray-500 mt-0.5">
              (client.py) The client component runs the <span className="text-orange-500 font-medium">Browser</span>-Use
              agent with a recording
            </div>
          </div>

          {/* Evaluations */}
          <div
            className="px-4 py-2.5 hover:bg-gray-50 cursor-pointer"
            style={{ animation: "fadeInUp 0.3s ease-out 0.6s both" }}
          >
            <div className="text-sm">Evaluations › Prerequisites</div>
            <div className="text-xs text-gray-500 mt-0.5"></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SearchOverlay;
