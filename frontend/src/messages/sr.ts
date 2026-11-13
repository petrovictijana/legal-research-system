/**
 * Centralised Serbian (Latin script) user-facing copy for Pravnislav.
 * All strings preserve č ć š ž đ. No English in the UI.
 */
export const sr = {
  brand: {
    wordmark: 'Pravnislav',
    tagline: 'Vaše pitanje. Odgovor. Izvor u zakonu.',
  },
  nav: {
    label: 'Glavna navigacija',
    menuOpen: 'Otvori meni',
    menuClose: 'Zatvori meni',
  },
  hero: {
    title: 'Pitaj Pravnislava',
    subtitle:
      'Postavite pitanje o zakonima i dobijte jasne odgovore zasnovane na zvaničnim pravnim dokumentima.',
  },
  examples: {
    // Styled uppercase in CSS; the accessible name stays natural case.
    heading: 'Primeri pitanja',
    prompts: [
      {
        id: 'godisnji-odmor',
        question: 'Koliko dana godišnjeg odmora imam prema zakonu?',
      },
      {
        id: 'registracija',
        question: 'Kako se registruje privredno društvo u Srbiji?',
      },
      {
        id: 'porodiljsko',
        question: 'Koja su prava roditelja na porodiljskom odsustvu?',
      },
      {
        id: 'zimske-gume',
        question: 'Kada je obavezno imati zimske gume na vozilu?',
      },
    ],
  },
  composer: {
    label: 'Vaše pravno pitanje',
    placeholder: 'Unesite vaše pitanje ovde...',
    helper: 'Enter šalje, Shift+Enter novi red.',
    submitAccessibleName: 'Pošalji pitanje',
    validationEmpty: 'Unesite pitanje pre slanja.',
  },
  chat: {
    loading: 'Tražim odgovor…',
    aiBadge: 'AI odgovor',
    aiDisclaimer: 'Automatski odgovor, nije zvaničan izvor ni pravni savet.',
    mockNotice: 'Demo odgovor — još bez pristupa pravnoj bazi.',
    error: 'Nije moguće dobiti odgovor. Pokušajte ponovo.',
    retry: 'Pokušajte ponovo',
    sourcesHeading: 'Izvori',
    articleLabel: 'član',
  },
  disclaimer: {
    // Shown beneath the composer on the landing screen (matches the design).
    ai: 'Odgovori su generisani uz pomoć veštačke inteligencije i zasnovani na dostupnim pravnim izvorima.',
    learnMore: 'Saznajte više',
    learnMoreHide: 'Prikaži manje',
    // Revealed inline by the "Saznajte više" control — no invented route.
    aiDetails:
      'Pravnislav koristi veštačku inteligenciju da objasni pravne teme na osnovu dostupnih izvora. Odgovori mogu biti nepotpuni ili netačni i ne predstavljaju pravni savet. Za obavezujuće informacije proverite zvanične izvore ili se obratite stručnjaku.',
  },
  mockAnswer:
    'Demo odgovor. Pravnislav još nije povezan sa pravnom bazom, pa ne navodi stvarne izvore. Kada bude povezan, ovde ćete videti objašnjenje sa citatima zakona i članova.',
} as const;
