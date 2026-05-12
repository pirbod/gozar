import type { Contact } from "../types/chat";

export const localUser = {
  id: "local-user",
  displayName: "You",
};

export const mockContacts: Contact[] = [
  {
    id: "sara",
    displayName: "Sara",
    handle: "sara",
    avatarInitials: "SA",
    presence: "available",
    safetyNumber: "48102 77018 33645 90812 66310 44592",
    verified: true,
  },
  {
    id: "arman",
    displayName: "Arman",
    handle: "arman",
    avatarInitials: "AR",
    presence: "away",
    safetyNumber: "33945 10882 77409 22018 55103 90177",
    verified: true,
  },
  {
    id: "mina",
    displayName: "Mina",
    handle: "mina",
    avatarInitials: "MI",
    presence: "offline",
    safetyNumber: "90551 22094 18180 77441 01883 49021",
    verified: false,
  },
  {
    id: "reza",
    displayName: "Reza",
    handle: "reza",
    avatarInitials: "RE",
    presence: "available",
    safetyNumber: "11890 45022 88013 44906 33027 77210",
    verified: true,
  },
  {
    id: "gorz-notes",
    displayName: "Gorz Notes",
    handle: "notes",
    avatarInitials: "GN",
    presence: "available",
    safetyNumber: "00000 11111 22222 33333 44444 55555",
    verified: true,
  },
];
