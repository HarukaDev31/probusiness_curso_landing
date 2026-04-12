/** Convierte código tipo `mar2026` → "marzo 2026" para títulos y meta. */
const MONTH: Record<string, string> = {
  ene: "enero",
  feb: "febrero",
  mar: "marzo",
  abr: "abril",
  may: "mayo",
  jun: "junio",
  jul: "julio",
  ago: "agosto",
  sep: "septiembre",
  oct: "octubre",
  nov: "noviembre",
  dic: "diciembre",
};

export function campaignHumanPeriod(codigo: string): string {
  const m = codigo.match(/^([a-z]{3})(\d{4})$/i);
  if (!m) return codigo;
  const month = MONTH[m[1].toLowerCase()] ?? m[1];
  return `${month} ${m[2]}`;
}
