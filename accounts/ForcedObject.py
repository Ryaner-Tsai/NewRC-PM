import numpy as np
from numpy import array as ar
from scipy.spatial import ConvexHull
# import matplotlib.pyplot as plt
from shapely.geometry import Point as sh_pt
# from shapely.geometry.polygon import Polygon as sh_poly
from shapely.geometry import asPolygon as sh_as_poly
from shapely.geometry import asLineString as sh_as_line
from matplotlib import pyplot as plt


class coordinate:
    def __init__(self, X, Y):
        if (X.shape == Y.shape) & (X.ndim == 1) & (Y.ndim == 1):
            self.X = X.copy()
            self.Y = Y.copy()
            self.XY = np.transpose(np.vstack([self.X, self.Y]))
            self.IsNG = 0
        else:
            self.X = np.zeros(X.shape)
            self.Y = np.zeros(Y.shape)
            self.XY = np.transpose(np.vstack([self.X, self.Y]))
            self.IsNG = 1

    def rotate(self, Angle, IsDegree=1):

        # step1.角度轉為徑度
        if IsDegree == 1:
            Angle = np.radians(Angle)

        # step2.利用徑度求出角度旋轉矩陣RotateRoot
        RotateRoot = ar([[np.cos(Angle), -np.sin(Angle)], [np.sin(Angle), np.cos(Angle)]])

        # step3.將X,Y合成為待旋轉座標 CoorDisRotated
        CoorDisRotated = np.vstack([self.X, self.Y])

        # step4.將np.matmul(RotateRoot,CoorDisRotated)求出CoorRotated
        CoorRotated = np.matmul(RotateRoot, CoorDisRotated)

        # step5. XRotated=CoorRotated[0,:]
        XRotated = CoorRotated[0, :]
        YRotated = CoorRotated[1, :]
        return self.__class__(XRotated, YRotated)

    def plot(self, X=0, Y=0):
        if X == 0 & Y == 0:
            plt.plot(self.X, self.Y, 'g^')
        else:
            plt.plot(X, Y, 'g^')
        plt.show()


class polygon(coordinate):

    def __init__(self, X, Y):
        def centroid_cal(XY, X, Y):
            return (sh_as_poly(XY).centroid.x, sh_as_poly(XY).centroid.y)

        def area_cal(x, y):
            return 0.5 * np.abs(np.sum(x * np.roll(y, -1)) - np.sum(y * np.roll(x, -1)))

        def polygonize(XY):
            # 取出座標群XY中，最外緣的多邊形，並將該多邊形以逆時針排序
            # XY[ConvexHull(XY).vertices,0] =XxCounterClock;exsample =[1,-1-3,-3,0.5]
            # XY[ConvexHull(XY).vertices,1]=YyCounterClock;exsample =[1,5,0.5,-1.5,-1.5]
            return np.transpose(np.vstack([XY[ConvexHull(XY).vertices, 0], XY[ConvexHull(XY).vertices, 1]]))

        super().__init__(X, Y)
        self.XY = polygonize(self.XY)
        self.X = np.transpose(self.XY[:, 0])
        self.Y = np.transpose(self.XY[:, 1])
        self.Centroid = centroid_cal(self.XY, self.X, self.Y)
        self.Area = area_cal(self.X, self.Y)

    def is_outside(self, Points):
        Polygon = sh_as_poly(self.XY)
        IsOutside = np.zeros(Points.shape[0])

        for i in range(Points.shape[0]):
            IsOutside[i] = Polygon.disjoint(sh_pt(Points[i, 0], Points[i, 1]))

        return IsOutside


class rectangle(polygon):
    def __init__(self, X, Y):
        super().__init__(X[0:4], Y[0:4])

    # 再一個FUNCTION:輸出一個新POLYGON 剛好是切出來的上半部
    def y_cut(self, YValue):
        Rectangle = sh_as_poly(self.XY)
        LineLen = np.zeros(self.XY.shape[0])
        XYclose = np.vstack([self.XY, self.XY[0, :], np.zeros(self.XY[0, :].shape)])

        for i in range(self.XY.shape[0]):
            LineLen[i] = sh_as_line(ar(XYclose[-XYclose.shape[0] + i:-XYclose.shape[0] + i + 2, :])).length
        DioLen = np.sum(LineLen[0:2] ** 2) ** 0.5
        CutLine = sh_as_line(ar([[-DioLen, YValue], [DioLen, YValue]]))
        return ar(Rectangle.intersection(CutLine))

    def upper(self, YValue):
        XYUpper = np.vstack([self.XY[self.XY[:, 1] > YValue, :], self.y_cut(YValue)])
        return polygon(XYUpper[:, 0], XYUpper[:, 1])


class forced_object():
    def __init__(self):
        pass


class reinforcements(forced_object):
    E = 2.04 * (10 ** 6)
    MaxStrain = float('inf')
    TensionZoneStrain = -0.005

    def __init__(self, X, Y, As, Fy, Angle=0, TransType='Tie'):
        self.X = X
        self.Y = Y
        self.As = As
        self.Fy = Fy
        self.Angle = Angle
        self.TransType = TransType

    @property
    def YieldStrain(self):
        # @property Decorators 使我們可以在call YieldStrain這個function的時候，不需要加 "()" 也就是如下宣告
        # Reinforcements = reinforcements(X,Y,As,Fy,E)
        # Reinforcements.YieldStrain
        # 這樣的好處是，我不需要去浪費記憶體

        return self.Fy / self.E

    @property
    def Coordinate(self):
        # Angle must be degree not rad
        return coordinate(self.X, self.Y).rotate(self.Angle)

    @staticmethod
    def phi(StrainT, Strain1, Strain2, Phi1, Phi2):

        if StrainT >= Strain1:
            Phi = Phi1
        elif StrainT <= Strain2:
            Phi = Phi2
        else:
            Phi = ((Phi2 - Phi1) / (Strain1 - Strain2)) * (Strain1 - StrainT) + Phi1
        return Phi

    def strained(self, NaDeeps, AttrTypes, TopStrain, TopY):
        DisFromTops = TopY - self.Coordinate.Y
        # print(DisFromTops)
        for i, NaDeep in enumerate(NaDeeps):

            if AttrTypes[i] == 2:
                self._Strain = (TopStrain / NaDeep) * (NaDeep - DisFromTops)

            elif AttrTypes[i] == 1:
                self._Strain = -np.full(self.Coordinate.XY.shape[0], self.MaxStrain)
            else:
                self._Strain = np.full(self.Coordinate.XY.shape[0], TopStrain)
            FakeStrain = self._Strain.copy()
            IsOverYield = np.abs(FakeStrain) > self.YieldStrain
            IsCompression = FakeStrain > 0
            IsTension = FakeStrain < 0

            FakeStrain[IsOverYield * IsCompression] = self.YieldStrain[IsOverYield * IsCompression]
            FakeStrain[IsOverYield * IsTension] = -self.YieldStrain[IsOverYield * IsTension]
            self._Stress = FakeStrain * self.E
            StrainT = self._Strain[self.Coordinate.Y == np.min(self.Coordinate.Y)]
            CompressionZoneStrain = -self.YieldStrain[self.Coordinate.Y == np.min(self.Coordinate.Y)]
            self._Phi = self.phi(StrainT if StrainT.shape == () else StrainT[0],
                                 CompressionZoneStrain if CompressionZoneStrain.shape == () else CompressionZoneStrain[
                                     0],
                                 self.TensionZoneStrain,
                                 0.65 if self.TransType == 'Tie' else 0.75,
                                 0.9)
            yield

    @property
    def Strain(self):
        if hasattr(self, '_Strain'):
            return self._Strain

    @property
    def Stress(self):
        if hasattr(self, '_Stress'):
            return self._Stress

    @property
    def Phi(self):
        if hasattr(self, '_Phi'):
            return self._Phi

    @property
    def CompressionForce(self):
        return self.As * self.NonOverlapStress

    @property
    def NonOverlapStress(self):
        if hasattr(self, '_NonOverlapStress'):
            return self._NonOverlapStress


class stressblock:
    def __init__(self, Stress, Polygon):
        self.Stress = Stress
        self.Polygon = Polygon

    @property
    def CompressionForce(self):
        return self.Polygon.Area * self.Stress

    def copy(self):
        return stressblock(self.Stress, self.Polygon)


class concrete(forced_object):
    CompStrainLim = 0.003

    def __init__(self, B, H, fc, Angle=0, IsDegree=1):
        self.B = B
        self.H = H
        self.fc = fc
        self.Angle = Angle
        self.IsDegree = IsDegree

    @property
    def Abbr(self):
        abbr = 0.85 - 0.00022 * (self.fc - 560)
        abbr = 0.7 if (abbr < 0.7) else abbr
        abbr = 0.85 if (abbr > 0.85) else abbr
        return abbr

    @property
    def Beta(self):
        beta = 0.85 - 0.00071 * (self.fc - 280)
        beta = 0.85 if (self.fc <= 280) else beta
        beta = 0.65 if (self.fc >= 560) else beta
        return beta

    @property
    def Rectangle(self):
        return rectangle(ar([(self.B / 2), (-self.B / 2), (-self.B / 2), (self.B / 2)]),
                         ar([(self.H / 2), (self.H / 2), (-self.H / 2), (-self.H / 2)])).rotate(self.Angle,
                                                                                                self.IsDegree)

    def strained(self, NaDeeps, AttrTypes, TopY, HRotated):
        for NaDeep, AttrType in zip(NaDeeps, AttrTypes):
            self._Stress = self.Abbr * self.fc
            if AttrType == 2:
                if self.Beta * NaDeep > HRotated:
                    self._StressPolygon = polygon(self.Rectangle.X, self.Rectangle.Y)

                else:
                    self._StressPolygon = self.Rectangle.upper(TopY - self.Beta * NaDeep)
            elif AttrType == 1:
                self._Stress = None

            else:
                self._StressPolygon = polygon(self.Rectangle.X, self.Rectangle.Y)
            yield

    @property
    def Stress(self):
        if hasattr(self, '_Stress'):
            return self._Stress

    @property
    def StressPolygon(self):
        if hasattr(self, '_StressPolygon'):
            return self._StressPolygon

    @property
    def CompressionForce(self):
        return self.StressPolygon.Area * self.Stress if (self.StressPolygon and self.Stress) is not None else None


class strain_attr():

    def __init__(self, H, TopStrain, TopY, NaDeepRatios=np.hstack([0, np.arange(0.01, 1, 0.01), np.arange(1, 2, 0.1), np.arange(2, 10, 0.2), float('inf')])):
        self.NaDeepRatios = NaDeepRatios
        self.H = H
        self.TopStrain = TopStrain
        self.TopY = TopY

    @property
    def NaDeeps(self):
        return self.NaDeepRatios * self.H

    @property
    def AttrTypes(self):
        AttrTypes = np.zeros(self.NaDeeps.shape)
        AttrTypes[self.NaDeeps == 0] = 1
        AttrTypes[ar(self.NaDeeps != 0) * ar(self.NaDeeps != float('inf'))] = 2
        AttrTypes[self.NaDeeps == float('inf')] = 3
        return AttrTypes


class force_system:
    def __init__(self, Coordinate, CompressionForce, TakeMomentPoint=coordinate(ar([0]), ar([0]))):
        self.Coordinate = Coordinate
        self.CompressionForce = CompressionForce
        self.TakeMomentPoint = TakeMomentPoint

    @property
    def Mxx(self):
        return np.sum((self.Coordinate.Y - self.TakeMomentPoint.Y) * -1 * self.CompressionForce)

    @property
    def Myy(self):
        return np.sum((self.Coordinate.X - self.TakeMomentPoint.X) * 1 * self.CompressionForce)

    @property
    def CombineCompressionForce(self):
        return np.sum(self.CompressionForce)


class section:
    def __init__(self, B, H, fc, X, Y, As, Fy, Angle=0, IsDegree=1, TransType='Tie'):
        self.Concrete = concrete(B, H, fc, Angle, IsDegree)
        self.Reinforcements = reinforcements(X, Y, As, Fy, Angle, TransType)

    @property
    def StrainAttr(self):
        return strain_attr(np.max(self.Concrete.Rectangle.Y) - np.min(self.Concrete.Rectangle.Y),
                           self.Concrete.CompStrainLim
                           , np.max(self.Concrete.Rectangle.Y))

    def strained(self):
        GenReinforcements = self.Reinforcements.strained(self.StrainAttr.NaDeeps, self.StrainAttr.AttrTypes,
                                                         self.StrainAttr.TopStrain, self.StrainAttr.TopY)
        GenConcrete = self.Concrete.strained(self.StrainAttr.NaDeeps, self.StrainAttr.AttrTypes, self.StrainAttr.TopY,
                                             self.StrainAttr.H)

        return GenReinforcements, GenConcrete

    def stress_nonoverlapping(self):
        # Stress=Stress.copy()
        self.Reinforcements._NonOverlapStress = self.Reinforcements._Stress.copy()
        if self.Concrete.StressPolygon is not None:
            IsInside = self.Concrete.StressPolygon.is_outside(self.Reinforcements.Coordinate.XY).astype(bool) == False
            self.Reinforcements._NonOverlapStress[IsInside == True] = self.Reinforcements._NonOverlapStress[
                                                                          IsInside == True] - self.Concrete.Stress

    @property
    def ForceSystem(self):
        XRotated = np.hstack([ar(self.Concrete.StressPolygon.Centroid[0]), self.Reinforcements.Coordinate.X])
        YRotated = np.hstack([ar(self.Concrete.StressPolygon.Centroid[1]), self.Reinforcements.Coordinate.Y])
        Compression = np.hstack([ar(self.Concrete.CompressionForce), self.Reinforcements.CompressionForce])
        return force_system(coordinate(XRotated, YRotated).rotate(-self.Concrete.Angle), Compression)
