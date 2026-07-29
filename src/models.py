import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any

@dataclass
class AttributeScores:
    FOR: int = 10
    DES: int = 10
    CON: int = 10
    INT: int = 10
    SAB: int = 10
    CAR: int = 10

    def modifier(self, attr_name: str) -> int:
        val = getattr(self, attr_name.upper(), 10)
        return (val - 10) // 2

    def to_dict(self) -> Dict[str, int]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> 'AttributeScores':
        return cls(
            FOR=data.get("FOR", 10),
            DES=data.get("DES", 10),
            CON=data.get("CON", 10),
            INT=data.get("INT", 10),
            SAB=data.get("SAB", 10),
            CAR=data.get("CAR", 10)
        )

@dataclass
class ClassLevelInfo:
    class_name: str
    level: int = 1
    subclass_name: str = ""
    hp_gained_history: List[int] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClassLevelInfo':
        return cls(
            class_name=data.get("class_name", ""),
            level=data.get("level", 1),
            subclass_name=data.get("subclass_name", ""),
            hp_gained_history=data.get("hp_gained_history", [])
        )

@dataclass
class EvolutionLogEntry:
    level: int                       # Total character level after this entry
    class_name: str                  # Class being leveled up
    class_level: int                 # New level in this specific class
    hp_gained: int                   # HP gained at this level (roll + CON)
    hp_roll: int                     # Raw roll/average without CON mod
    features_unlocked: List[str]     # Features unlocked
    asi_or_feat: str                 # Stat increase or feat chosen
    spell_slots_unlocked: Dict[str, int] # e.g. {"1": 2}
    timestamp: str                   # Date/time formatted

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EvolutionLogEntry':
        return cls(
            level=data.get("level", 1),
            class_name=data.get("class_name", ""),
            class_level=data.get("class_level", 1),
            hp_gained=data.get("hp_gained", 0),
            hp_roll=data.get("hp_roll", 0),
            features_unlocked=data.get("features_unlocked", []),
            asi_or_feat=data.get("asi_or_feat", ""),
            spell_slots_unlocked=data.get("spell_slots_unlocked", {}),
            timestamp=data.get("timestamp", "")
        )

@dataclass
class SpellInfo:
    name: str
    level: int  # 0 for Truque
    school: str
    casting_time: str
    range_area: str
    components: str
    duration: str
    description: str
    classes: List[str]
    prepared: bool = False

@dataclass
class EquipmentItem:
    name: str
    quantity: int = 1
    weight: float = 0.0
    type: str = "Geral" # Arma, Armadura, Poção, Ferramenta, Geral
    description: str = ""
    damage: str = ""
    damage_type: str = ""
    properties: str = ""
    equipped: bool = False

@dataclass
class Character:
    id: Optional[int] = None
    name: str = "Novo Herói"
    campaign: str = "Campanha D&D 2024"
    species: str = "Humano"
    background: str = "Acólito"
    origin_feat: str = "Iniciado em Magia"
    alignment: str = "Neutro e Bom"
    classes: List[ClassLevelInfo] = field(default_factory=list)
    attributes: AttributeScores = field(default_factory=AttributeScores)

    # Proficiencias em Pericias (dict ex: {"Acrobacia": 1, "Atletismo": 2}) 0=Nao prof, 1=Proficiente, 2=Especialidade
    skill_proficiencies: Dict[str, int] = field(default_factory=dict)
    
    # Salvaguardas com proficiencia ex: ["FOR", "CON"]
    saving_throw_proficiencies: List[str] = field(default_factory=list)

    # Outras proficiências (Armas, Armaduras, Ferramentas, Idiomas)
    weapon_proficiencies: str = ""
    armor_proficiencies: str = ""
    tool_proficiencies: str = ""
    languages: str = "Comum"

    # Status vitais
    max_hp: int = 10
    current_hp: int = 10
    temp_hp: int = 0
    armor_class_override: Optional[int] = None # None se auto-calculado
    speed: int = 9 # metros (30ft = 9m)

    # Recursos e slots de magia consumidos ex: {"1": 1, "2": 0} (quantos foram gastos)
    used_spell_slots: Dict[str, int] = field(default_factory=dict)

    # Equipamentos e Inventario
    inventory: List[Dict[str, Any]] = field(default_factory=list)
    copper: int = 0
    silver: int = 0
    electrum: int = 0
    gold: int = 15
    platinum: int = 0

    # Magias conhecidas/preparadas
    spells: List[Dict[str, Any]] = field(default_factory=list)

    # Personalidade, Aparência, Notas
    notes: str = ""
    backstory: str = ""
    avatar_b64: str = ""

    # Histórico de Evolução por Nível (Imutável)
    evolution_log: List[EvolutionLogEntry] = field(default_factory=list)

    created_at: str = ""
    updated_at: str = ""

    @property
    def total_level(self) -> int:
        if not self.classes:
            return 1
        return sum(c.level for c in self.classes)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "campaign": self.campaign,
            "species": self.species,
            "background": self.background,
            "origin_feat": self.origin_feat,
            "alignment": self.alignment,
            "classes": [c.to_dict() for c in self.classes],
            "attributes": self.attributes.to_dict(),
            "skill_proficiencies": self.skill_proficiencies,
            "saving_throw_proficiencies": self.saving_throw_proficiencies,
            "weapon_proficiencies": self.weapon_proficiencies,
            "armor_proficiencies": self.armor_proficiencies,
            "tool_proficiencies": self.tool_proficiencies,
            "languages": self.languages,
            "max_hp": self.max_hp,
            "current_hp": self.current_hp,
            "temp_hp": self.temp_hp,
            "armor_class_override": self.armor_class_override,
            "speed": self.speed,
            "used_spell_slots": self.used_spell_slots,
            "inventory": self.inventory,
            "copper": self.copper,
            "silver": self.silver,
            "electrum": self.electrum,
            "gold": self.gold,
            "platinum": self.platinum,
            "spells": self.spells,
            "notes": self.notes,
            "backstory": self.backstory,
            "avatar_b64": self.avatar_b64,
            "evolution_log": [e.to_dict() for e in self.evolution_log],
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Character':
        classes = [ClassLevelInfo.from_dict(c) for c in data.get("classes", [])]
        attributes = AttributeScores.from_dict(data.get("attributes", {}))
        evolution_log = [EvolutionLogEntry.from_dict(e) for e in data.get("evolution_log", [])]

        return cls(
            id=data.get("id"),
            name=data.get("name", "Novo Herói"),
            campaign=data.get("campaign", ""),
            species=data.get("species", "Humano"),
            background=data.get("background", "Acólito"),
            origin_feat=data.get("origin_feat", ""),
            alignment=data.get("alignment", "Neutro"),
            classes=classes,
            attributes=attributes,
            skill_proficiencies=data.get("skill_proficiencies", {}),
            saving_throw_proficiencies=data.get("saving_throw_proficiencies", []),
            weapon_proficiencies=data.get("weapon_proficiencies", ""),
            armor_proficiencies=data.get("armor_proficiencies", ""),
            tool_proficiencies=data.get("tool_proficiencies", ""),
            languages=data.get("languages", "Comum"),
            max_hp=data.get("max_hp", 10),
            current_hp=data.get("current_hp", 10),
            temp_hp=data.get("temp_hp", 0),
            armor_class_override=data.get("armor_class_override"),
            speed=data.get("speed", 9),
            used_spell_slots=data.get("used_spell_slots", {}),
            inventory=data.get("inventory", []),
            copper=data.get("copper", 0),
            silver=data.get("silver", 0),
            electrum=data.get("electrum", 0),
            gold=data.get("gold", 15),
            platinum=data.get("platinum", 0),
            spells=data.get("spells", []),
            notes=data.get("notes", ""),
            backstory=data.get("backstory", ""),
            avatar_b64=data.get("avatar_b64", ""),
            evolution_log=evolution_log,
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", "")
        )
