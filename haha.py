class Entity:
    m_Pos = [1,0]

    def getPos(self):
        return self.m_Pos

def ProcessEntity(en : Entity):
    print(en.getPos())

en = Entity()
ProcessEntity(en)


