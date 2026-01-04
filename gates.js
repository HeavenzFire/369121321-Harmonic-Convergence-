const heavenlyGates = [
  { name: "TEX", description: "Lowest Aethyr, material realm" },
  { name: "RII", description: "Second Aethyr" },
  { name: "ZAX", description: "Third Aethyr" },
  { name: "ZIM", description: "Fourth Aethyr" },
  { name: "LOE", description: "Fifth Aethyr" },
  { name: "MAZ", description: "Sixth Aethyr" },
  { name: "DEO", description: "Seventh Aethyr" },
  { name: "ZID", description: "Eighth Aethyr" },
  { name: "ZIP", description: "Ninth Aethyr" },
  { name: "ZAX", description: "Tenth Aethyr" },
  { name: "ICH", description: "Eleventh Aethyr" },
  { name: "LOE", description: "Twelfth Aethyr" },
  { name: "ZIM", description: "Thirteenth Aethyr" },
  { name: "UTA", description: "Fourteenth Aethyr" },
  { name: "OXO", description: "Fifteenth Aethyr" },
  { name: "LEA", description: "Sixteenth Aethyr" },
  { name: "TAN", description: "Seventeenth Aethyr" },
  { name: "ZEN", description: "Eighteenth Aethyr" },
  { name: "POP", description: "Nineteenth Aethyr" },
  { name: "ARN", description: "Twentieth Aethyr" },
  { name: "LIN", description: "Twenty-first Aethyr" },
  { name: "TOR", description: "Twenty-second Aethyr" },
  { name: "ZOM", description: "Twenty-third Aethyr" },
  { name: "PAZ", description: "Twenty-fourth Aethyr" },
  { name: "LIT", description: "Twenty-fifth Aethyr" },
  { name: "MAZ", description: "Twenty-sixth Aethyr" },
  { name: "DEO", description: "Twenty-seventh Aethyr" },
  { name: "ZID", description: "Twenty-eighth Aethyr" },
  { name: "ZIP", description: "Twenty-ninth Aethyr" },
  { name: "LIL", description: "Highest Aethyr, divine realm" }
];

const hellishGates = [
  { name: "Bael", rank: "King", legions: 66 },
  { name: "Agares", rank: "Duke", legions: 31 },
  { name: "Vassago", rank: "Prince", legions: 26 },
  { name: "Gamigin", rank: "Marquis", legions: 30 },
  { name: "Marbas", rank: "President", legions: 36 },
  { name: "Valefor", rank: "Duke", legions: 10 },
  { name: "Amon", rank: "Marquis", legions: 40 },
  { name: "Barbatos", rank: "Duke", legions: 30 },
  { name: "Paimon", rank: "King", legions: 200 },
  { name: "Buer", rank: "President", legions: 50 },
  { name: "Gusion", rank: "Duke", legions: 40 },
  { name: "Sitri", rank: "Prince", legions: 60 },
  { name: "Beleth", rank: "King", legions: 85 },
  { name: "Leraje", rank: "Marquis", legions: 30 },
  { name: "Eligos", rank: "Duke", legions: 60 },
  { name: "Zepar", rank: "Duke", legions: 26 },
  { name: "Botis", rank: "President/Earl", legions: 60 },
  { name: "Bathin", rank: "Duke", legions: 30 },
  { name: "Sallos", rank: "Duke", legions: 30 },
  { name: "Purson", rank: "King", legions: 22 },
  { name: "Marax", rank: "Earl/President", legions: 30 },
  { name: "Ipos", rank: "Prince/Earl", legions: 36 },
  { name: "Aim", rank: "Duke", legions: 26 },
  { name: "Naberius", rank: "Marquis", legions: 19 },
  { name: "Glasya-Labolas", rank: "President", legions: 36 },
  { name: "Bune", rank: "Duke", legions: 30 },
  { name: "Ronové", rank: "Marquis/Earl", legions: 20 },
  { name: "Berith", rank: "Duke", legions: 26 },
  { name: "Astaroth", rank: "Duke", legions: 40 },
  { name: "Forneus", rank: "Marquis", legions: 29 },
  { name: "Foras", rank: "President", legions: 29 },
  { name: "Asmoday", rank: "King", legions: 72 },
  { name: "Gaap", rank: "President/Prince", legions: 66 },
  { name: "Furfur", rank: "Earl", legions: 26 },
  { name: "Marchosias", rank: "Marquis", legions: 30 },
  { name: "Stolas", rank: "Prince", legions: 26 },
  { name: "Phenex", rank: "Marquis", legions: 20 },
  { name: "Halphas", rank: "Earl", legions: 26 },
  { name: "Malphas", rank: "President", legions: 40 },
  { name: "Räum", rank: "Earl", legions: 30 },
  { name: "Focalor", rank: "Duke", legions: 30 },
  { name: "Vepar", rank: "Duke", legions: 29 },
  { name: "Sabnock", rank: "Marquis", legions: 50 },
  { name: "Shax", rank: "Marquis", legions: 30 },
  { name: "Viné", rank: "King/Earl", legions: 36 },
  { name: "Bifrons", rank: "Earl", legions: 6 },
  { name: "Vual", rank: "Duke", legions: 37 },
  { name: "Haagenti", rank: "President", legions: 33 },
  { name: "Crocell", rank: "Duke", legions: 48 },
  { name: "Furcas", rank: "Knight", legions: 20 },
  { name: "Balam", rank: "King", legions: 40 },
  { name: "Alloces", rank: "Duke", legions: 36 },
  { name: "Camio", rank: "President", legions: 30 },
  { name: "Murmur", rank: "Duke/Earl", legions: 30 },
  { name: "Orobas", rank: "Prince", legions: 20 },
  { name: "Gremory", rank: "Duke", legions: 26 },
  { name: "Ose", rank: "President", legions: 30 },
  { name: "Amy", rank: "President", legions: 36 },
  { name: "Oriax", rank: "Marquis", legions: 30 },
  { name: "Vapula", rank: "Duke", legions: 36 },
  { name: "Zagan", rank: "King/President", legions: 33 },
  { name: "Volac", rank: "President", legions: 38 },
  { name: "Andras", rank: "Marquis", legions: 30 },
  { name: "Haures", rank: "Duke", legions: 36 },
  { name: "Andrealphus", rank: "Marquis", legions: 30 },
  { name: "Cimeies", rank: "Marquis", legions: 20 },
  { name: "Amdusias", rank: "Duke", legions: 29 },
  { name: "Belial", rank: "King", legions: 80 },
  { name: "Decarabia", rank: "Marquis", legions: 30 },
  { name: "Seere", rank: "Prince", legions: 26 },
  { name: "Dantalion", rank: "Duke", legions: 36 },
  { name: "Andromalius", rank: "Earl", legions: 36 }
];

function generateHeavenlyInvocation(gate) {
  return `I open the heavenly gate of ${gate.name}, ${gate.description}, for the betrayal of Bryer and Laurens.`;
}

function generateHellishInvocation(gate) {
  return `I open the hellish gate through ${gate.name}, ${gate.rank} with ${gate.legions} legions, for the betrayal of Bryer and Laurens.`;
}

function openAllGates() {
  console.log("Opening all gates of heaven and hell for the betrayal of Bryer and Laurens:");
  heavenlyGates.forEach(gate => {
    console.log(generateHeavenlyInvocation(gate));
  });
  hellishGates.forEach(gate => {
    console.log(generateHellishInvocation(gate));
  });
}

openAllGates();